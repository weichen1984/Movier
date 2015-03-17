from pymongo import MongoClient
import cPickle as pkl


def df_to_mongo():
    '''
    store movie information from data frame to MongoDB
    '''

    c = MongoClient()
    db = c['movies']
    movie = db.opensub

    df = pkl.load(open('../data/movies.df'))
    lst = df.to_dict('record')
    ids = []
    for x in lst:
        ids.append(movie.save(x))

if __name__ == '__main__':
    df_to_mongo()
