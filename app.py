from firebase_admin import credentials, firestore, auth
import firebase_admin
import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from process_files.process import extract_data

UPLOAD_FOLDER = 'docs'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

cred = credentials.Certificate("firebase_credentials.json")
firebase_app = firebase_admin.initialize_app(cred)
if not firebase_admin._apps:
    print("Firebase not Initialized!")
db = firestore.client()

uid = "pjNLWcuSoxGqV8Lby1QD"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return "Hello World"

@app.route('/upload', methods=['GET', 'POST'])
def documentAnalysis():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            data = extract_data(UPLOAD_FOLDER + '/' + filename)
            return f"<p>{data}</p>"
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
