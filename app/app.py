from flask import Flask, request, redirect, url_for
from flask import render_template
from werkzeug import secure_filename
import dill as pickle
import numpy as np
import pandas as pd
from globs import *
from helper import *
import os
import locale

app = Flask(__name__)
locale.setlocale( locale.LC_ALL, '' )

def form_predict_page(lst, indices):
    '''
    construct webpage from the template
    '''
    with open('templates/predict_page.html', 'r') as f:
        return f.read() % tuple(lst + indices)

@app.route('/')
def index():
    # return '<h1> Something </h1>'
    return render_template('index.html')


UPLOAD_FOLDER = "upload/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/pickamovie', methods=['GET'])
def submission():
    return render_template("pickamovie.html")
    # return '''
    #     <!doctype html>
    #     <title>Pick A Movie</title>
    #     <h1>Upload a subtitle/script text file</h1>
    #     <form action="/predict" method=post enctype=multipart/form-data>
    #       <p><input type=file name=file>
    #          <input type=submit value=Upload>
    #     </form>
    #     <p> Note: for now you have to download english subtitles from 
    #         <a href="http://www.opensubtitles.org" target="_blank">opensubtitles.org</a> or 
    #         <a href="http://subscene.com" target="_blank">subscene.com</a> 
    #         and upload here to make a prediction. 
    #     </p>
    # '''

model = pickle.load(open('model/movier.pkl', 'rb'))
rfr = pickle.load(open('model/rfr.pkl', 'rb'))

@app.route('/predict', methods=['GET', 'POST'] )
def predict_page():
    global fsave
    # get data from request form, the key is the name you set in your form
    try:
        fl = request.files['file']
        if fl and request.method == "POST":
            fn = secure_filename(fl.filename)
            fsave = os.path.join(app.config['UPLOAD_FOLDER'], fn)
            fl.save(fsave)
    except:
        pass

    # clean and tokenize the input file
    text = extract_file(fsave)
    os.remove(fsave)
    text = ' '.join(tokenize(clean([text])[0]))
    W = model.transform_predict([text])
    bo_pred = rfr.predict(W)

    # find the top 5 labeld topics and corresponding topic names
    # as well as value of each topic
    sorted_indices = np.argsort(W)[0][::-1]
    count = 0
    indices = []
    top_topics = []
    val_topics = []
    for index in sorted_indices:
        if index in topics:
            indices.append(index)
            top_topics.append(topics[index])
            val_topics.append(W[0][index])
            count += 1
        if count >= 5:
            break
    other = ("Others", W[0].sum() - sum(val_topics))

    data = {"textwords30": ' '.join(text.split()[:100]) + ' ...',
            "topicwords20": [(topic, ', '.join(model.top_words[50][index][:20])) \
                            for index, topic in zip(indices, top_topics)],
            "indices": indices, 
            "topics": top_topics, 
            "values": zip(top_topics, val_topics), 
            "bo_pred": locale.currency(int(bo_pred), grouping=True),
            "other": other}
    return render_template("predict_page.html", **data)


@app.route('/trends', methods=['GET', 'POST'] )
def trend_page():
    info = zip(topic_indices, topic_names, topic_colors)
    data = {"info": info}
    return render_template('trends.html', **data)
    # with open('templates/trends.html') as f:
    #     return f.read()

@app.route('/about', methods=['GET','POST'])
def about_page():
    # with open('templates/about.html') as f:
    #     return f.read()
    return render_template('about.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)