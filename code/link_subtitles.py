import pandas as pd
import numpy as np
import cPickle as pkl


def match_subtitles():
    '''
    match the subtitles provided by opensubtitles.org with our US feature
    movie list; flag the movies whether or not there are subtitles available
    '''

    # load the pickled data frame from fetch_movie.py
    df_movies = pkl.load(open('../data/movies.df'))

    # load the subtitle information provided by opensubtitles.org into a
    # data frame from export.txt
    df_subtitles = pd.read_csv('../data/export.txt', delimiter='\t')

    # Only take the following two columns
    df = df_subtitles[['IDSubtitleFile', 'MovieImdbID']]

    # Group subtitles for the movies with the same IMDb ID together and get
    # one of the subtitles for each movie
    df = df.groupby('MovieImdbID').min()

    # Movies with subtitles available
    movie_with_subs = set(df.index)

    # Flag movies whether or not there are subtitles available and store the
    # information to the initial data frame
    cond = df_movies['id'].astype(int).isin(movie_with_subs)
    df_movies['flag'] = cond
    df_movies['sub_id'] = np.nan
    df_movies.loc[cond, 'sub_id'] = \
        df.loc[df_movies[cond]['id'].astype(int)].values

    # Re-store the data frame
    pkl.dump(df_movies, open('../data/movies.df', 'wb'))

if __name__ == '__main__':
    match_subtitles()
