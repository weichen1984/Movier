from pymongo import MongoClient
from bs4 import BeautifulSoup as BS
import numpy as np

c = MongoClient()

db = c['movies']
opensub = db.opensub
missing = db.missing
omdb = db.omdb
movie_info = db.movie_info


def get_genre(html):
    '''
    get genre from the stored html texts
    '''

    soup = BS(html, 'html.parser')
    try:
        return [x.strip() for x in
                soup.find_all('span', class_='genre')[0].text.split('|')]
    except:
        print 'no genre class'
        return None


def get_boxoffice(text):
    '''
    get boxoffice information i.e. parse $5.4M to 5400000
    '''

    if text == 'N/A':
        return None
    else:
        text = text.strip('$')
        if 'M' in text:
            return 1000000 * float(text.replace('M', ''))
        elif 'k' in text:
            return 1000 * float(text.replace('k', ''))
        else:
            return float(text)


def add_opensub():
    '''
    add the movies stored in MongoDB.opensub
    '''

    r = opensub.find({'flag': True})
    for x in r:
        y = x.copy()
        y.pop('flag')
        y.pop('sub_id')
        y['url'] = 'http://www.imdb.com/title/tt' + y['id'] + '/'
        y['genre'] = get_genre(y['title_text'])
        movie_info.save(y)


def add_subscene():
    '''
    add the movies stored in MongoDB.subscene
    '''

    r = missing.find({'flag': True})
    for x in r:
        nid = x['_id']
        y = opensub.find_one({'_id': nid}).copy()
        y.pop('flag')
        y.pop('sub_id')
        y['url'] = 'http://www.imdb.com/title/tt' + y['id'] + '/'
        y['genre'] = get_genre(y['title_text'])
        movie_info.save(y)


def add_omdb_info():
    '''
    add Plot and BoxOffice information scraped from omdb
    '''

    r = omdb.find({}, {'_id': 1, 'Plot': 1, 'BoxOffice': 1})
    for x in r:
        nid = x['_id']
        query = {'$set': {'Plot': x['Plot'],
                          'BoxOffice': get_boxoffice(x['BoxOffice'])}}
        movie_info.update({'_id': nid}, query)


def main():
    add_opensub()
    add_subscene()
    add_omdb_info()


if __name__ == '__main__':
    main()
