import dill
import pandas as pd
import numpy as np
from pymongo import MongoClient
from sklearn.linear_model import Ridge
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.ensemble import RandomForestRegressor as RFR


def get_data():
    '''
    get the predictor and target and return them
    '''

    nids = dill.load(open('movie_ids.pkl', 'rb'))
    model = dill.load(open('all2.pkl', 'rb'))
    W = model.W
    df = pd.DataFrame(W, index=nids)

    c = MongoClient()
    db = c['movies']
    boxoffice2 = db.boxoffice2
    movie_info = db.movie_info

    r = list(boxoffice2.find({}, {'_id': 1, 'BoxOffice2': 1}))
    df_bf = pd.DataFrame(r).set_index('_id')

    r2 = list(movie_info.find({}, {'_id': 1, 'year': 1, 'title': 1}))
    df_year = pd.DataFrame(r2)
    df_year = df_year.set_index('_id')

    df = df.join(df_bf).join(df_year)

    cond1 = (df['year'] >= 2010)
    cond2 = ~ np.isnan(df['BoxOffice2'])

    cond = cond1 & cond2

    df_subset = df[cond]
    y = df_subset['BoxOffice2'].values
    X = df_subset.iloc[:, :-3].values

    return X, y


def grid_search(X, y):
    '''
    cross validated grid search using Ridge Regressor and Random
    Forest Regressor
    '''

    nids = df_subset.index
    titles = df_subset['title']

    pars = {'alpha': [0.8, 0.6, 0.5, 0.45, 0.4, 0.2, 0.1,
                      0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02]}

    gs = GridSearchCV(Ridge(), pars, cv=5)
    gs.fit(X, y)

    ridge = gs.best_estimator_
    dill.dump(ridge, open('ridge.pkl', 'wb'))

    pars = {'max_depth': [5, 8, 10, 20, 50, 100],
            'min_samples_split': [2, 3, 5, 10, 20]}

    gs = GridSearchCV(RFR(n_estimators=100, random_state=42, n_jobs=2),
                      pars, cv=5)
    rfr = gs.best_estimator_
    dill.dump(rfr, open('rfr.pkl', 'wb'))
    return ridge, rfr


if __name__ == '__main__':
    X, y = get_data()
    ridge, rfr = grid_search(X, y)
