from movier2 import Movier
import pandas as pd
import os


indir = "../data/txt/raw/"
outdir = "../data/txt/clean_w/"
a = Movier()


def clean_year(year):
    '''
    clean the raw subtitle text from srt_to_txt for the year specified
    '''

    fn = 'subtext' + str(year)
    df = pd.read_csv(indir + fn, dtype=str, delimiter='\t', header=None)
    mids = df.iloc[:, 0].values
    docs = df.iloc[:, 1].values
    if os.path.exists(outdir + fn):
        return
    with open(outdir + fn, 'w') as fout:
        for mid, doc in zip(mids, docs):
            print 'year %s: %s' % (year, mid)
            text = ' '.join(a.tokenize(a.clean([doc])[0]))
            fout.write(mid + '\t' + text + '\n')


def clean_years(years):
    '''
    clean the raw subtitle text from srt_to_txt for the years specified
    '''

    for year in years:
        print 'year = ', year
        clean_year(year)


if __name__ == '__main__':
    clean_years(range(1914, 2015))
