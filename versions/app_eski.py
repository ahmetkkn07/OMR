from flask import Flask, render_template
import os
from flask import flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import time

# UPLOAD_FOLDER = '/temp/images/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/uploadAnswerKey")
def uploadAnswerKey():
    UPLOAD_FOLDER = '/temp/images/' + str(time.time()).replace(".", "-")

    # str(time.time()).replace(".", "-")
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    print(app.config['UPLOAD_FOLDER'])
    return render_template("uploadAnswerKey.html")


if __name__ == "__main__":
    app.run()
