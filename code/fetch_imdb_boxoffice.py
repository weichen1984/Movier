import requests
from bs4 import BeautifulSoup as BS
from pymongo import MongoClient
import dill
import pandas as pd
import re


def fetch_imdb_boxoffice():
    '''
    fetch box office information from the business page on imdb.com
    '''

    c = MongoClient()
    db = c['movies']
    movie_info = db.movie_info
    boxoffice2 = db.boxoffice2
    r = list(movie_info.find({}, {'_id':1, 'url':1}))
    df = pd.DataFrame(r)
    n_movies = df.shape[0]

    df = df.set_index('_id')
    indices = df.index
    regex = re.compile('[0-9][0-9,]+')
    for i in indices:
        print '.',
        if boxoffice2.find({'_id': int(i)}).count() == 0:
            url = df.loc[i, 'url'] + 'business'
            rs = requests.get(url)
            if rs.status_code == 200:
                soup = BS(rs.content, 'html.parser')
                x = soup.find('h5', text='Gross')
                if x:
                    y = x.next_sibling
                    if '(USA)' in y:
                        bf = int(regex.findall(y)[0].replace(',', ''))
                    else:
                        print 'No US box office available'
                        bf = None
                else:
                    print 'No box office available'
                    bf = None
            else:
                print 'Movie %s no business page' % i
                bf = None
            boxoffice2.save({'_id': int(i), 'BoxOffice2': bf})


if __name__ == '__main__':
    fetch_imdb_boxoffice()
