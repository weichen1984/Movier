import io
import re
import chardet
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import SnowballStemmer

stemmer = SnowballStemmer("english")


def check_text(line):
    '''
    check if each line of srt file is text
    if a line is pure digit, return an empty string
    if a line is time line, return an empty string also
    otherwise, return the text
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


def extract_text(fn, encoding):
    '''
    extract text from srt with the given encoding system
    use check_text to extract text for each line of the file
    '''
    tt = []
    with io.open(fn, 'r', encoding=encoding) as g:
        lines = g.readlines()
        for x in lines:
            y = check_text(x)
            if y:
                tt.append(y)
        text = ' '.join(tt).strip()
    return text


def extract_file(fn):
    '''
    extract text from srt file using extract_text after
    finding the encoding system
    this function is neccessary since files come in with
    all kinds of encoding
    '''
    try:
        f = open(fn)
        content = f.read()
        f.close()
        r = chardet.detect(content)
        charenc = r['encoding']
        text = extract_text(fn, charenc)
    except:
        charenc = None
        text = extract_text(fn, charenc)

    return text


def clean(docs):
    '''
    get rid of <> and {} tags, links (with and without)
    '''
    regex = re.compile('{\d+}' +            # { } tags
                       '|' +
                       '\w+\.com' +         # xxx.com: partial link
                       '|' +
                       '<.+?>' +            # < > tags
                       '|' +
                       # below get rid of other link
                       '((([A-Za-z]{3,9}:' +
                       '(?:\/\/)?)' +
                       '(?:[\-;:&=\+\$,\w]+@)?' +
                       '[A-Za-z0-9\.\-]+' +
                       '|' +
                       '(?:www\.' +
                       '|' +
                       '[\-;:&=\+\$,\w]+@)' +
                       '[A-Za-z0-9\.\-]+)' +
                       '((?:\/[\+~%\/\.\w\-_]*)?\??' +
                       '(?:[\-\+=&;%@\.\w_]*)#?' +
                       '(?:[\.\!\/\\\w]*))?)')
    return [regex.sub(' ', doc) for doc in docs]


def tokenize(doc):
    '''
    use NLTK RegexpTokenizer
    '''
    tokenizer = RegexpTokenizer("\w{3,}")
    return [stemmer.stem(x) for x in tokenizer.tokenize(doc)]
