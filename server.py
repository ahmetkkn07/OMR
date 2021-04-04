import os
from flask import Flask, session, flash, request, redirect, render_template, url_for
from werkzeug.utils import secure_filename
import time
import shutil
from flask_fontawesome import FontAwesome
import omr
from wtforms import Form, StringField, PasswordField, validators
import database as db
from datetime import datetime

app = Flask(__name__)
fa = FontAwesome(app)

app.secret_key = "secret_key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
ANSWER_LETTERS = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: '-', 6: 'X'}

# CLASSES


class RegistrationForm(Form):
    name = StringField('Ad', [validators.Length(min=2, max=35)])
    surname = StringField('Soyad', [validators.Length(min=2, max=35)])
    email = StringField('Eposta', [validators.Length(min=6, max=100)])
    password = PasswordField('Şifre', [
        validators.DataRequired(),
        validators.EqualTo(
            'password', message='Girdiğiniz şifreler eşleşmiyor!')
    ])
    confirm = PasswordField('Şifreyi Tekrar Girin')


class LoginForm(Form):
    email = StringField('Eposta', [validators.Length(min=6, max=100)])
    password = PasswordField('Şifre', [validators.DataRequired()])

# FUNCTIONS


def createUploadDirectory():
    path = os.getcwd()
    UPLOAD_FOLDER = os.path.join(
        path, 'static/uploads/') + str(int(time.time()))
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


def isLoggedIn():
    if 'login' in session:
        return session['login']
    else:
        return False


def getUser():
    temp = session['user']
    user = {
        "name": temp[0],
        "surname": temp[1],
        "email": temp[2],
        "password": temp[3]
    }
    return user

# RENDER TEMPLATES


@app.route('/register', methods=['GET', 'POST'])
@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = (form.name.data, form.surname.data, form.email.data,
                form.password.data)
        if db.register(user[0], user[1], user[2], user[3]):
            flash('Kayıt başarılı, giriş yapabilirsiniz', 'success')
            print("Kayıt başarılı")
            return redirect(url_for('login'), code=302)
        flash('Kayıt yapılamadı, daha önce aynı eposta ile kaydolmadığınızdan emin olun!', 'error')
    return render_template('register.html', form=form, page='register', login=isLoggedIn())


@app.route('/login', methods=['GET', 'POST'])
@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = (form.email.data, form.password.data)
        if db.login(user[0], user[1]):
            session['login'] = True
            session['user'] = db.getUserByEmail(user[0])
            flash('Başarıyla giriş yaptınız.', 'success')
            return redirect('/')
        flash('Giriş yapılamadı, eposta ve şifrenizi kontrol edin!', 'error')
    return render_template('login.html', form=form, page='login', login=isLoggedIn())


@app.route('/')
def run():
    session.pop('_flashes', None)
    if 'UPLOAD_FOLDER' in session:
        session.pop('UPLOAD_FOLDER', None)
    # deleteUploadDirectory()
    return render_template('index.html', page='index', login=isLoggedIn())


@app.route('/usage')
def usage():
    session.pop('_flashes', None)
    # deleteUploadDirectory()
    return render_template('usage.html', page='usage', login=isLoggedIn())


@app.route('/uploadAnswerKey')
def upload_answer():
    if isLoggedIn():
        # deleteUploadDirectory()
        createUploadDirectory()
        return render_template('uploadAnswerKey.html', login=isLoggedIn())
    else:
        flash('Bu işlemi gerçekleştirmek için giriş yapmalısınız!', 'error')
        return redirect(url_for('login'))


@app.route('/completed')
def completed():
    if isLoggedIn():
        return render_template('completed.html', scores=session['SCORES'], answer_key=session['ANSWERS_STR'], login=isLoggedIn())
    else:
        flash('Bu işlemi gerçekleştirmek için giriş yapmalısınız!', 'error')
        return redirect(url_for('login'))


@app.route('/uploadPapers')
def upload_form():
    if isLoggedIn():
        return render_template('uploadPapers.html', answer_key=session['ANSWERS_STR'], login=isLoggedIn())
    else:
        flash('Bu işlemi gerçekleştirmek için giriş yapmalısınız!', 'error')
        return redirect(url_for('login'))


@app.route('/account')
@app.route('/account/')
def account():
    if isLoggedIn():
        session.pop('_flashes', None)
        operations = list()
        temp = db.getOperationsByEmail(getUser()["email"])
        if temp is not None:
            operations = list(temp)
            for ind, op in enumerate(operations):
                operations[ind] = list(op)
                operations[ind].append(datetime.fromtimestamp(
                    int(op[0])))
                operations[ind].append(len(db.getRecordsById(op[0])))
        return render_template('account.html', user=getUser(), operations=operations, page='account', login=isLoggedIn())
    else:
        flash('Bu işlemi gerçekleştirmek için giriş yapmalısınız!', 'error')
        return redirect(url_for('login'))


@app.route('/detail')
def detail():
    if isLoggedIn():
        session.pop('_flashes', None)
        id = request.args.get('id')
        answerKey = db.getOperationById(id)[2]
        records = list()
        temp = db.getRecordsById(id)
        if temp is not None:
            records = list(temp)
        return render_template('detail.html', user=getUser(), records=records, answer_key=answerKey, page='detail', login=isLoggedIn())
    else:
        flash('Bu işlemi gerçekleştirmek için giriş yapmalısınız!', 'error')
        return redirect(url_for('login'))

# REDIRECTS


@app.route('/logout', methods=['GET', 'POST'])
@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    if 'login' in session:
        session.pop('login', None)
    if 'user' in session:
        session.pop('user', None)
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect('/')


@app.route('/uploadAnswerKey', methods=['POST'])
def uploadAnswerKey():
    if isLoggedIn():
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
                # deleteUploadDirectory()
                flash('Yüklediğiniz dosya uzantısı desteklenmemektedir. Desteklenen dosya uzantılarını (.jpg .png .jpeg) kullanınız.', 'error')
                return redirect(request.url)
        except:
            # deleteUploadDirectory()
            flash('Yüklediğiniz cevap anahtarı standartlara uygun olmadığı için isteğiniz işlenemiyor. Lütfen standartlara uygun bir cevap anahtarı kullanınız.', 'error')
            return redirect(request.url)
        flash('Cevap anahtarı başarıyla yüklendi.', 'success')
        return redirect('/uploadPapers')
    else:
        flash('Bu işlemi gerçekleştirmek için giriş yapmalısınız!', 'error')
        return redirect(url_for('login'))


@app.route('/uploadPapers', methods=['POST'])
def uploadPapers():
    if isLoggedIn():
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
                    db.addOperation(session['UPLOAD_FOLDER'], getUser()[
                        "email"], session['ANSWERS_STR'])
                    db.addRecord(session['UPLOAD_FOLDER'], result[1], result[3],
                                 result[4], result[5], result[0], ANSWERS_STR, result[2])
                else:
                    flash(
                        'Yüklediğiniz dosya uzantısı desteklenmemektedir. Desteklenen dosya uzantılarını (.jpg .png .jpeg) kullanınız.', 'error')
                    return redirect(request.url)
        except:
            flash('Yüklediğiniz sınav kağıtlarının arasında standartlara uygun olmayanlar bulunduğu için isteğiniz işlenemiyor. Lütfen standartlara uygun kağıtları kullanınız.', 'error')
            return redirect(request.url)
        session['SCORES'] = SCORES
        flash('Dosyalar başarıyla yüklendi.', 'success')
        return redirect('/completed')
    else:
        flash('Bu işlemi gerçekleştirmek için giriş yapmalısınız!', 'error')
        return redirect(url_for('login'))


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    app.run(host='0.0.0.0', port=80, debug=False, threaded=True)
