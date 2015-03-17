import os
import sys
import requests
import zipfile
from bs4 import BeautifulSoup as BS
import cPickle as pickle
import pandas as pd
import numpy as np
import re
from pymongo import MongoClient
from string import punctuation


def download_file(url, mid, path):
    '''
    Downloads and extracts the url content to the specified path with
    a name same as IMDb id (mid) .
    '''

    response = requests.get(url, stream=True)
    with open('subtitle.zip', 'wb') as out_file:
        fsrc = response.raw
        size = response.headers.get("content-length")
        length = 16 * 1024
        while True:
            buf = fsrc.read(length)
            if not buf:
                break
            out_file.write(buf)
            sys.stdout.write("Downloaded " +
                             str(os.path.getsize('subtitle.zip')/1024) +
                             "kb of " + str(int(size)/1024) +
                             " kb\r")
            sys.stdout.flush()
        print "\nDownload complete\nExtracting"
    del response

    # check if the downloaded file is zip file and is good to extract
    try:
        zipf = zipfile.ZipFile('subtitle.zip')
        fns = zipf.namelist()
        for x in fns:
            if x[-4:] == '.srt':
                fn = x
                break
        fn = fns[0]
        zipf.extract(fn, path)
        zipf.close()
        if path[-1] != '/':
            path += '/'
        os.rename(path+fn, path+mid+'.srt')
        os.remove('subtitle.zip')
    except:
        print "* The subtitle file is not good to extract."
        return False
    return True


def check_exist(url):
    '''
    check if the request url return any results, some movies exist but
    no English subtitles are available
    '''

    r = requests.get(url)
    soup = BS(r.content)
    del r
    td = soup.find('td', class_='a1')
    return td


def replace_special_characters(title):
    '''
    Remove punctuation from titles for the movies been searched
    '''

    for c in punctuation:
        title = title.replace(c, ' ')
    return title


def find_alternative_link(movie_title,
                          year,
                          subtitle_language,
                          wrong_year=False):
    '''
    Find alternative link for the movies that don't have an exact name or year
    match. Subscene.com sometimes stored a movie with a slightly different name
    '''

    # Get all the request results
    title_query = '+'.join(movie_title.lower().split())
    query = "http://subscene.com/subtitles/title?q=" \
            + title_query \
            + '&l=' \
            + subtitle_language
    r = requests.get(query)
    soup = BS(r.content)
    del r
    tags = soup.find_all('div', class_='title')

    # Find the one that matches the movie and release year
    titles = [x.text.strip() for x in tags]

    # Exact name exists but not year, so find the one with correct year
    if wrong_year:
        title = movie_title + ' (' + str(year) + ')'
        indices = np.where(titles == title)[0]
        if indices.any():
            index = indices[0]
            tag = tags[index]
            url = 'http://subscene.com' \
                  + tag.find('a')['href'] \
                  + '/' + subtitle_language
            if check_exist(url) is not None:
                return True, url, \
                    'Wrong year, but exact subtitles exist'
            else:
                return False, None, \
                    'Page exists but no subtitles are available'
        else:
            return False, None, \
                'Wrong year, and no subtitles are available'

    # Exact name does not exist but find the match in a different name
    else:
        for i, tt in enumerate(titles):
            if (movie_title in tt) & (str(year) in tt):
                tag = tags[i]
                url = 'http://subscene.com' \
                      + tag.find('a')['href'] \
                      + '/' + subtitle_language
                if check_exist(url) is not None:
                    return True, url, \
                        'Exact match does not exist, but alternative does'
                else:
                    return False, None, \
                        'Alternative page exists but no subtitles available'
        return False, None, 'No match found'  # history: No subtitle


def find_link(movie_title, year, subtitle_language='english'):
    '''
    find the link for the movie with name and year specified
    '''

    movie_title = replace_special_characters(movie_title)
    title_query = '-'.join(movie_title.lower().split())
    url = "http://subscene.com/subtitles/" \
          + title_query + '/' + subtitle_language
    r = requests.get(url)
    if r.status_code == 200:
        soup = BS(r.content)
        del r
        td = soup.find('td', class_='a1')
        if td is None:
            print 'Page exists but no subtitles are available'
            return False, None, 'Page exists but no subtitles are available'
        else:
            web_year = int(soup.find('div', class_='header')
                               .find('ul').find('li').text.split()[1])
            if year in range(web_year-2, web_year+3):
                return True, url, 'Exact subtitles exist'
            else:
                print 'wrong year'
                return find_alternative_link(movie_title, year,
                                             subtitle_language,
                                             wrong_year=True)
    else:
        print 'scraping subtitle link fail'
        del r
        return find_alternative_link(movie_title, year, subtitle_language)


def get_download_link(url):
    '''
    get the download link from the url specified
    '''

    r1 = requests.get(url)
    sp1 = BS(r1.content)
    td = sp1.find('td', class_='a1')
    a = td.find('a')
    surl = 'http://subscene.com' + a['href']
    r2 = requests.get(surl)
    sp2 = BS(r2.content)
    div = sp2.find('div', class_='download')
    download_url = 'http://subscene.com' + div.find('a')['href']
    return download_url


def fetch_missing_subtitle(years):
    '''
    fetch subtitles for years specified in argument years
    '''

    # store information of these missing subtitles in MongoDB subscene
    c = MongoClient()
    db = c['movies']
    missing = db.subscene
    movies = pickle.load(open('../data/movies.df'))

    for year in years:
        count = 0
        outdir = '../data/subscene_subtitles/' + str(year)
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        cond1 = movies['year'] == year
        cond2 = ~ movies['flag']
        cond = cond1 & cond2
        movie = movies[cond][['id', 'year', 'title', '_id']]
        nids = movie['_id']
        mids = movie['id']
        titles = movie['title']

        for nid, mid, title in zip(nids, mids, titles):
            count += 1
            # check if the subtitle has been downloaded
            if missing.find({'_id': nid}).count() == 0:
                print year, count
                dct = {'_id': nid, 'id': mid, 'year': year, 'title': title}
                flg, surl, comment = find_link(title, year)
                dct['comment'] = comment
                if flg:
                    url = get_download_link(surl)
                    dct['download_url'] = url
                    dct['flag'] = download_file(url, mid, outdir)
                else:
                    dct['flag'] = flg

                missing.save(dct)

if __name__ == '__main__':
    fetch_missing_subtitle(range(2014, 1873, -1))
