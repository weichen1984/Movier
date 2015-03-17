from string import punctuation
from pymongo import MongoClient
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd
import re
from nltk.tokenize import RegexpTokenizer
import dill as pickle
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer


class Movier(object):

    def __init__(self,
                 kw_tfidf={},
                 kw_nmf={}):
        self.kw_tfidf = kw_tfidf
        self.kw_nmf = kw_nmf
        self.tfidf = None
        self.nmf = None
        self.top_words = {}
        self.stemmer = SnowballStemmer("english")


    def clean(self, docs):
        '''
        get rid of <> and {} tags, links (with and without)
        '''

        regex = re.compile('{\d+}|\w+\.com|<.+?>|'
            + '((([A-Za-z]{3,9}:(?:\/\/)?)'
            + '(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|'
            + '(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)'
            + '((?:\/[\+~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_]*)#?'
            + '(?:[\.\!\/\\\w]*))?)')
        return [regex.sub(' ', doc) for doc in docs]


    def tokenize(self, doc):
        '''
        use NLTK RegexpTokenizer
        '''

        tokenizer = RegexpTokenizer("\w{3,}")
        return [self.stemmer.stem(x) for x in tokenizer.tokenize(doc)]


    def fit(self, docs, clean=False):
        '''
        pipeline: clean, tokenize, tfidf, nmf, kmeans
        '''

        if clean:
            print 'cleaning raw docs ......'
            clean_docs = self.clean(docs)
        else:
            clean_docs = docs

        print 'running tfidf ......'
        if 'tokenizer' not in self.kw_tfidf:
            self.tfidf = TfidfVectorizer(tokenizer=self.tokenize,
                                         **self.kw_tfidf)
        else:
            self.tfidf = TfidfVectorizer(**self.kw_tfidf)
        X = self.tfidf.fit_transform(clean_docs)

        print 'running NMF ......'
        self.nmf = NMF(**self.kw_nmf)
        H = self.nmf.fit_transform(X)
        W = self.nmf.components_

        print 'fetching top 50 words for each topic ......'
        self.top_n_words(50, W)

        return X, H, W


    def transfrom_predict(self, docs):
        '''
        transform and predict based on raw text from docs
        return the corresponding H matrix
        '''

        X = self.tfidf.transform(docs)
        H = self.nmf.transform(X)
        return H



    def top_n_words(self, n):
        '''
        find the top n frequent words for each feature
        '''

        if n in self.top_words:
            return self.top_words[n]
        else:
            self.top_words[n] = {}
            k = self.H.shape[0]
            words = np.array(self.tfidf.get_feature_names())
            for i in xrange(k):
                indices = np.argsort(self.H[i])[-1:(-n-1):-1]
                self.top_words[n][i] = list(words[indices])


def load_data():
    '''
    load
    '''

    fdir = '../data/txt/clean_w/'
    dfs = []
    for year in xrange(1914, 2015):
        if year % 10 == 0:
            print 'year = %s' % year
        dft = pd.read_csv(fdir + 'subtext' + str(year), delimiter='\t', header=None)
        dfs.append(dft)
    df = pd.concat(dfs, axis=0)
    return df


def build_all():
    df = load_data()
    docs = list(df.iloc[:, 1].values)
    kw_tfidf = {'max_df': 0.9, 'stop_words': 'english', 'min_df':0.015, 'tokenizer':None, 'token_pattern': "\w{3,}"}
    kw_nmf = {'n_components': 200, 'max_iter': 300}
    kw_kmeans = {'n_clusters': 30}
    model = Movier(kw_tfidf=kw_tfidf, kw_nmf=kw_nmf, kw_kmeans=kw_kmeans)
    model.fit(docs)
    pickle.dump(model, open('all_maxdf09.pkl', 'wb'))

if __name__ == '__main__':
    # build_model(40)
    build_all()








