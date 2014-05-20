import os
import random
from flask import Flask, request, redirect, url_for, send_from_directory, session, render_template, Response, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(__name__)


app.config.update(dict(
    SERVICE_URL='localhost:5000',
    UPLOAD_FOLDER='private',
    PUBLIC_FOLDER='public',
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'docx', 'doc', 'png', 'jpeg', 'jpg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if session['logged_in']:
        if request.method == 'POST':
            public = False
            if request.form['public'] == "True":
                public = True
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                name = ''.join(random.choice('abcdefghijklmnopqrstuvwzyzABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(6)) +"."+ filename.rsplit('.', 1)[1]
                while name in os.listdir(app.config['UPLOAD_FOLDER']):
                    name = ''.join(random.choice('abcdefghijklmnopqrstuvwzyzABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(6)) +"."+ filename.rsplit('.', 1)[1]
                if not public:
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], name))
                else:
                    file.save(os.path.join(app.config['PUBLIC_FOLDER'], name))
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], name))
                return render_template('success.html', filename=filename, name=name, public=public)
        return '''
        <!doctype html>
        <h1>Upload new File</h1>
        <form action="" method=post enctype=multipart/form-data>
          <p><input type=file name=file>
             <input type=submit value=Upload><input type="checkbox" name="public" value="True">public
        </form>
        '''
    return redirect(url_for('login'))
@app.route('/upload/<filename>')
def uploaded_file(filename):
    if session['logged_in']:
        return send_from_directory(app.config['UPLOAD_FOLDER'],filename)
    else:
        return redirect(url_for('login'))
@app.route('/')
def serve_index():
    if session.get('logged_in'):
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        #print files
        #return str(files)
        return render_template('index.html', files=files)
    return redirect(url_for('login'))
@app.route('/login', methods=['POST','GET'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid Username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid Password'
        else:
            session['username'] = request.form['username']
            session['logged_in'] = True
            return redirect(url_for('serve_index'))
    return render_template('login.html', error=error)
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

"""
API
"""

@app.route('/api/list')
@requires_auth
def auth_index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return files

@app.route('/api/upload', methods='POST')
@requires_auth
def auth_upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
@app.route('/api/public/list')
def public_list():
    files = os.listdir(app.config['PUBLIC_FOLDER'])
    response = jsonify(files=files)
    return response
if __name__ == '__main__':
    app.run(host='0.0.0.0')
