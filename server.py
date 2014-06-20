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
	USER_FILE='users.cfg',
	FILE_CONF='allowed_files.cfg'
))
USERS = {}
for line in open(app.config['USER_FILE'], 'r'):
	if len(line.split(":")) == 2:
		users[line.split(":")[0]] = line.split(":")[1].strip()
ALLOWED_EXTENSIONS = []
for line in open(app.config['FILE_CONF'], 'r'):
	if len(line.strip()) < 0:
		ALLOWED_EXTENSIONS.append(line.strip())
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
		try:
			if USERS[request.form['username']] == request.form['password']:
				session['username'] = request.form['username']
				session['logged_in'] = True
				return redirect(url_for('serve_index'))
			else:
				error = 'Invalid Password'
		except:
			error = 'Invalid Username'
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.run(host='0.0.0.0')