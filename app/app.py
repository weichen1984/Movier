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

# set locale to format box office number into currency
locale.setlocale(locale.LC_ALL, '')


# index page
@app.route('/')
def index():
    return render_template('index.html')


# project description page
@app.route('/about', methods=['GET', 'POST'])
def about_page():
    return render_template('about.html')


# set the folder to temporarily store the uploaded files
# file will be deleted after a new file is uploaded
UPLOAD_FOLDER = "upload/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# upload page
@app.route('/pickamovie', methods=['GET'])
def submission():
    return render_template("pickamovie.html")


# load the machine learning models and store them as
# global variable so no need to load multiple times
model = pickle.load(open('model/movier.pkl', 'rb'))
rfr = pickle.load(open('model/rfr.pkl', 'rb'))


# response page after the upload page
@app.route('/predict', methods=['GET', 'POST'])
def predict_page():

    # fsave is the variable that stores the path of the uploaded file
    # making it global so that reloading this page does not throw error
    global fsave

    # get data from request form, the key is the name you set in your form
    try:
        fl = request.files['file']
        if fl and request.method == "POST":
            fn = secure_filename(fl.filename)
            # if a new file is uploaded, the old file will be deleted
            if "fsave" in globals():
                os.remove(fsave)
            fsave = os.path.join(app.config['UPLOAD_FOLDER'], fn)
            fl.save(fsave)
    except:
        pass

    # clean and tokenize the input file
    try:

        # if first time running the webpage go to the error_page
        fsave

        # model prediction based on uploaded file
        text = extract_file(fsave)
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

        # data that will be passed down to the prediction page and
        # be used by Jinja2
        data = {"textwords30": ' '.join(text.split()[:100]) + ' ...',
                "topicwords20": [(topic,
                                  ', '.join(model.top_words[50][index][:20])
                                  )
                                 for index, topic in zip(indices, top_topics)],
                "indices": indices,
                "topics": top_topics,
                "values": zip(top_topics, val_topics),
                "bo_pred": locale.currency(int(bo_pred), grouping=True)
                }

        # direct to the predict_page
        return render_template("predict_page.html", **data)

    except:

        # direct to the error_page if no file has been uploaded yet
        return render_template("error_page.html")


# trend page, the info are imported from globs.py
@app.route('/trends', methods=['GET', 'POST'])
def trend_page():
    info = zip(topic_indices, topic_names, topic_colors)
    data = {"info": info}
    return render_template('trends.html', **data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
