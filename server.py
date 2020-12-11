import os
from flask import Flask, session, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import time
import shutil
from flask_fontawesome import FontAwesome
import omr

app = Flask(__name__)
fa = FontAwesome(app)

app.secret_key = "secret_key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
ANSWER_LETTERS = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: '-', 6: 'X'}


def createUploadDirectory():

    path = os.getcwd()
    UPLOAD_FOLDER = os.path.join(path, 'static/uploads/') + str(time.time())
    if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    session['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def deleteUploadDirectory():
    if 'UPLOAD_FOLDER' in session:
        if os.path.isdir(session['UPLOAD_FOLDER']):
            shutil.rmtree(session['UPLOAD_FOLDER'])
        session['UPLOAD_FOLDER'] = ''
    if 'SCORES' in session:
        session['SCORES'] = ''


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/clearData', methods=['GET'])
def clearData():
    session.pop('_flashes', None)
    deleteUploadDirectory()


@app.route('/')
def run():
    session.pop('_flashes', None)
    deleteUploadDirectory()
    return render_template('index.html', page='index')


@app.route('/usage')
def usage():
    session.pop('_flashes', None)
    deleteUploadDirectory()
    return render_template('usage.html', page='usage')


@app.route('/uploadAnswerKey')
def upload_answer():
    deleteUploadDirectory()
    createUploadDirectory()
    return render_template('uploadAnswerKey.html')


@app.route('/uploadAnswerKey', methods=['POST'])
def uploadAnswerKey():
    try:
        file = request.files.get('file')
        ANSWER_KEY = list()
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(session['UPLOAD_FOLDER'], filename))

            ANSWER_KEY = omr.getAnswers(
                session['UPLOAD_FOLDER'] + '/' + filename)
            session['ANSWER_KEY'] = ANSWER_KEY

            ANSWERS_STR = ''
            for ans in ANSWER_KEY:
                ANSWERS_STR += (ANSWER_LETTERS[ans])
            session['ANSWERS_STR'] = ANSWERS_STR
        else:
            deleteUploadDirectory()
            flash('Yüklediğiniz dosya uzantısı desteklenmemektedir. Desteklenen dosya uzantılarını (.jpg .png .jpeg) kullanınız.', 'error')
            return redirect(request.url)
    except:
        deleteUploadDirectory()
        flash('Yüklediğiniz cevap anahtarı standartlara uygun olmadığı için isteğiniz işlenemiyor. Lütfen standartlara uygun bir cevap anahtarı kullanınız.', 'error')
        return redirect(request.url)
    flash('Cevap anahtarı başarıyla yüklendi.', 'success')
    return redirect('/uploadPapers')


@app.route('/uploadPapers')
def upload_form():
    return render_template('uploadPapers.html', answer_key=session['ANSWERS_STR'])


@app.route('/uploadPapers', methods=['POST'])
def uploadPapers():
    try:
        files = request.files.getlist('files[]')
        SCORES = {}
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(session['UPLOAD_FOLDER'], filename))

                temp = list()
                temp.clear()

                ANSWERS_STR = ''
                for ans in omr.getAnswers(
                        session['UPLOAD_FOLDER'] + '/' + filename):
                    ANSWERS_STR += (ANSWER_LETTERS[ans])
                temp.append(ANSWERS_STR)

                result = omr.getScores(
                    (session['UPLOAD_FOLDER'] + '/' + filename), session['ANSWER_KEY'], session['UPLOAD_FOLDER'])
                temp.append(result[0])
                print(result[1])
                temp.append('static' + (result[1].split('static')[1]))
                temp.append(result[3])
                temp.append(result[4])
                temp.append(result[5])

                SCORES[result[2]] = temp
                """
                    scores[0] = cevap şıkları
                    scores[1] = puan
                    scores[2] = ad soyad img
                    scores[3] = correct
                    scores[4] = wrong
                    scores[5] = empty
                """
            else:
                flash('Yüklediğiniz dosya uzantısı desteklenmemektedir. Desteklenen dosya uzantılarını (.jpg .png .jpeg) kullanınız.', 'error')
                return redirect(request.url)
    except:
        flash('Yüklediğiniz sınav kağıtlarının arasında standartlara uygun olmayanlar bulunduğu için isteğiniz işlenemiyor. Lütfen standartlara uygun kağıtları kullanınız.', 'error')
        return redirect(request.url)
    session['SCORES'] = SCORES
    flash('Dosyalar başarıyla yüklendi.', 'success')
    return redirect('/completed')


@app.route('/completed')
def completed():
    return render_template('completed.html', scores=session['SCORES'], answer_key=session['ANSWERS_STR'])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    # app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
