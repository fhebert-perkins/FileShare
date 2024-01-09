import os
import random
from flask import Flask, request, redirect, url_for, send_from_directory, session, render_template, Response, jsonify
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
	SERVICE_URL='localhost:8080',
	UPLOAD_FOLDER='private',
	PUBLIC_FOLDER='public',
	DEBUG=True,
	SECRET_KEY='development key',
	USER_FILE='users.cfg',
	FILE_CONF='allowed_files.cfg'
))

file_text = open("users.json", "r")
USERS = json.loads(file_text.read())
file_text.close() # JSON (JavaScript Object Notation) is more efficient and flexible

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
			if "True" in request.form.keys(): # If the checkbox is not checked the nothing would be returned so by using in you can account for this error
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
		<form action="/upload" method="post" enctype="multipart/form-data">
		  	<input type=file name=file>
			<input type=submit value=Upload>
			<input type="checkbox" name="public" value="True"><label>public</label>
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
				error = 'Invalid Password' # Change to "Invalid Credencial", its safer because it prevents user enumeration attacks
		except:
			error = 'Invalid Username' # Change to "Invalid Credencial", its safer because it prevents user enumeration attacks
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080, debug=True)