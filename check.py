def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST' and session['']:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
@app.route('/upload/<filename>')
def uploaded_file(filename):
    if session['logged_in']:
    	return send_from_directory(app.config['UPLOAD_FOLDER'],
                               	filename)
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
@app.route('/api/<path>')
def api(path):
	if path == get