from string import punctuation
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from pymongo import MongoClient
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd
import re
from nltk.tokenize import RegexpTokenizer
import dill as pickle
from nltk.corpus import names, stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
from sklearn.manifold import MDS
from sklearn.metrics.pairwise import cosine_similarity
# import cPickle as pickle




# def clean(docs):
#     '''
#     get rid of <> and {} tags, links (with and without)
#     '''
#     regex = re.compile('{\d+}|\w+\.com|<.+?>|((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_]*)#?(?:[\.\!\/\\\w]*))?)')
#     return [regex.sub(' ', doc) for doc in docs]


# def tokenize(doc):
#     '''
#     use NLTK RegexpTokenizer
#     '''
#     tokenizer = RegexpTokenizer("[\w'\.\-]{2,}\w")
#     return [stemmer.stem(x) for x in tokenizer.tokenize(doc)]


# def fit_tfidf(docs, **kwarg):


class Movier(object):

    def __init__(self, 
                 kw_tfidf={}, 
                 kw_nmf={}, 
                 kw_kmeans={}):
        self.kw_tfidf = kw_tfidf
        self.kw_nmf = kw_nmf
        self.kw_kmeans = kw_kmeans
        # self.tokenizer = None
        self.tfidf = None
        self.nmf = None
        self.kmean = None
        self.top_words = {}
        self.coords = None
        self.stemmer = SnowballStemmer("english")
        

    def clean(self, docs):
        '''
        get rid of <> and {} tags, links (with and without)
        '''
        regex = re.compile('{\d+}|\w+\.com|<.+?>|((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_]*)#?(?:[\.\!\/\\\w]*))?)')
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
            self.tfidf = TfidfVectorizer(tokenizer=self.tokenize, **self.kw_tfidf)
        else:
            self.tfidf = TfidfVectorizer(**self.kw_tfidf)
        self.X = self.tfidf.fit_transform(clean_docs)
        

        print 'running NMF ......'
        self.nmf = NMF(**self.kw_nmf)
        self.W = self.nmf.fit_transform(self.X)
        self.H = self.nmf.components_

        print 'running KMeans ......'
        self.kmeans = KMeans(**self.kw_kmeans)
        self.kmeans.fit(self.X)

        # print 'running MDS ......'
        # self.mds = MDS(n_components=2, dissimilarity='precomputed', random_state=1)
        # dist = 1 - cosine_similarity(self.W)
        # self.coords = self.mds.fit_transform(dist)

        # print 'running 2nd Kmeans ......'
        # dist1 = 1 - cosine_similarity(self.X)
        # self.kmeans2 = KMeans(**self.kw_kmeans)
        # self.kmeans2.fit(self.X)

        # print 'running 2nd MDS ......'
        # self.mds2 = MDS(n_components=2, dissimilarity='precomputed', random_state=1)
        # dist2 = 1 - cosine_similarity(self.X)
        # self.coords2 = self.mds2.fit_transform(dist2)

        self.top_n_words(50)

    def transfrom_predict(self, docs):
        X = self.tfidf.transform(docs)
        W = self.nmf.transform(X)
        ic = self.kmeans.predict(X)
        return W, ic
        


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




# def clean(docs):
#     '''
#     get rid of <> and {} tags, links (with and without)
#     '''
#     regex = re.compile('{\d+}|\w+\.com|<.+?>|((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_]*)#?(?:[\.\!\/\\\w]*))?)')
#     return [regex.sub(' ', doc) for doc in docs]


# def tokenize(doc):
#     '''
#     use NLTK RegexpTokenizer
#     '''
#     tokenizer = RegexpTokenizer("[\w'\.\-]{2,}\w")
#     return [stemmer.stem(x) for x in tokenizer.tokenize(doc)]


def random_load_data(n):
    fdir = '../data/txt/clean_w/'
    dfs = []
    for year in xrange(1914, 2015):
        print 'year = %s' % year
        dft = pd.read_csv(fdir + 'subtext' + str(year), delimiter='\t', header=None)
        n_movies = dft.shape[0]
        if n_movies <= n:
            dfs.append(dft)
        else:
            indices = np.random.choice(n_movies, n, replace=False)
            dfs.append(dft.iloc[indices])
    df = pd.concat(dfs, axis=0)
    return df

# def main():
#     df = pd.read_csv('../data/txt/clean/subtext2013', delimiter='\t')
#     docs = list(df.iloc[:, 1].values)
#     kw_tfidf = {'max_df': 0.8, 'stop_words': 'english', 'min_df':10, 'ngram_range':(1,1)}
#     kw_nmf = {'n_components': 100, 'max_iter': 300}
#     kw_kmeans = {'n_clusters': 20}
#     model = Movier(kw_tfidf=kw_tfidf, kw_nmf=kw_nmf, kw_kmeans=kw_kmeans)
#     model.fit(docs)
#     # model.pickler('model2013.pkl')
#     pickle.dump(model, open('model2013_nmf100iter300_2methods.pkl', 'w'))


def build_model(n):
    df = random_load_data(n)
    docs = list(df.iloc[:, 1].values)
    kw_tfidf = {'max_df': 0.8, 'stop_words': 'english', 'min_df':0.015, 'tokenizer':None, 'token_pattern': "[\w'\.\-]{2,}\w"}
    kw_nmf = {'n_components': 100, 'max_iter': 300}
    kw_kmeans = {'n_clusters': 20}
    model = Movier(kw_tfidf=kw_tfidf, kw_nmf=kw_nmf, kw_kmeans=kw_kmeans)
    model.fit(docs)
    pickle.dump(model, open('random40.pkl', 'wb'))


def load_data():
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








