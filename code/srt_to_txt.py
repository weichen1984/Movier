import os
import io
import chardet
import rarfile
import shutil
from pymongo import MongoClient


c = MongoClient()
db = c['movies']
encode = db.encode

srt_dir = "../data/srt/"
raw_dir = "../data/txt/raw/"


def check_text(line):
    '''
    check if the line is digit, timeline, or text
    '''

    line = line.strip()
    if '-->' in line or line == '':
        return ''
    else:
        line = line.encode('ascii', 'ignore')
        if line.isdigit():
            return ''
        else:
            return ' '.join(line.split())


def extract_text(fn, path, encoding):
    '''
    extract text for file fn with specified encoding
    '''

    tt = []
    with io.open(path + fn, 'r', encoding=encoding) as g:
        lines = g.readlines()
        for x in lines:
            y = check_text(x)
            if y:
                tt.append(y)
        text = ' '.join(tt).strip()
    return text


def extract_file(fn, path):
    '''
    find the encoding and extract text for file fn
    '''

    mid = fn.replace('.srt', '')
    nid = int(mid)
    if encode.find({'_id': nid}).count() != 0:
        charenc = list(encode.find({'_id': nid}))[0]['encode']
        text = extract_text(fn, path, charenc)
        return mid, text
    else:
        try:
            f = open(path + fn)
            content = f.read()
            f.close()
            r = chardet.detect(content)
            charenc = r['encoding']
            text = extract_text(fn, path, charenc)
        except:
            try:
                charenc = None
                text = extract_text(fn, path, charenc)
            except:
                fn1 = mid + '.rar'
                os.rename(path + fn, path + fn1)
                rf = rarfile.RarFile(path + fn1)
                for f in rf.infolist():
                    filename = f.filename
                    if filename[-4:] == '.srt':
                        break
                rf.extract(filename, path)
                os.rename(path + filename, path + fn)
                shutil.copy2(path + fn1, path + '../rar/' + fn1)
                return extract_file(fn, path)

        encode.save({'_id': nid, 'id': mid, 'encode': charenc})
        return mid, text


def extract_year(year):
    '''
    extract text from srt files for year specified
    '''

    path = srt_dir + str(year) + '/'
    fns = os.listdir(path)
    with open(raw_dir + 'subtext' + str(year), 'w') as fout:
        for fn in fns:
            if fn[-4:] == '.srt':
                print 'year = ' + str(year) + 'parsing ' + fn
                mid, text = extract_file(fn, path)
                fout.write(mid + '\t' + text + '\n')


def extract_years(years):
    '''
    extract text from srt files for years specified
    '''

    for year in years:
        print 'year = ', year
        extract_year(year)


if __name__ == '__main__':
    extract_years(range(2014, 1873))
