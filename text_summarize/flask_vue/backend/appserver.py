# from newsapi.application import create_app
#
#
# if __name__=='__main__':
#     app = create_app()
#     app.run()

from flask import Flask, render_template
from flask_cors import CORS
from flask import request
from flask import jsonify
import sys
import json

from keywords import KeyWord
from summa import SenVec


app = Flask(__name__,
            static_folder="../frontend/summarization/dist/static",
            template_folder="../frontend/summarization/dist/")

CORS(app)

keyword = None
senvec = None
def init():
    global keyword
    global senvec
    keyword = KeyWord(words=5)
    senvec = SenVec()

init()

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")


@app.route('/generate', methods=['GET', 'POST'])
def get_news():
    global keyword
    if request.method == 'POST':

        raw_data = request.data
        text = json.loads(raw_data)["text"]

        print(text, file=sys.stdout)

        top_words = keyword.extract(text)
        top_sens = senvec.summarization(text)[:5]
        # print(request.get_data(), file=sys.stdout)


    return jsonify(keywords=top_words, summa=top_sens)
