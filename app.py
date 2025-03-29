from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
import extract
from process import process_file_content
from firebase_admin import credentials, firestore, auth
import firebase_admin
from process_files.process import gemini_call


cred = credentials.Certificate("firebase_credentials.json")
firebase_app = firebase_admin.initialize_app(cred)
if not firebase_admin._apps:
    print("Firebase not Initialized!")
db = firestore.client()

app = Flask(__name__)
app.secret_key = 'ac5ab744684a0585c7bde4a3285057468440df322d09c61f6986621d62301f3f'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# Home Route
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('upload'))
    return redirect(url_for('login'))


# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            # Create user in Firebase Auth
            user = auth.create_user(email=email, password=password)
            session['user_email'] = email

            # Save user data to Firestore
            db.collection('users').document(user.uid).set({
                'email': email,
                'uid': user.uid
            })

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Registration failed: {e}", "danger")

    return render_template('register.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        try:
            user = auth.get_user_by_email(email)
            session['user_id'] = user.uid
            session['user_email'] = email
            return redirect(url_for('upload'))
        except Exception as e:
            flash(f"Login failed: {e}", "danger")

    return render_template('login.html')


# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # Check if user is logged in
    username = session.get('user_id')
    if not username:
        flash('Please log in to upload files.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        files = request.files.getlist('file')

        if not files or files[0].filename == '':
            flash('No files selected.', 'error')
            return redirect(request.url)

        extracted_contents = []
        for file in files:
            try:
                # Extract data using extract.py
                content = extract.extract_data(file, file.filename)

                # Append username to filename to prevent conflicts
                filename = f"{username}_{file.filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                # Save file
                file.save(file_path)

                extracted_contents.append(process_file_content(content))
            except Exception as e:
                flash(f"Error processing {file.filename}: {str(e)}", 'error')

        if not extracted_contents:
            flash('No valid files to process.', 'error')
            return redirect(request.url)
        # Return extracted data for now
        data = gemini_call(extracted_contents)
        return data

    return render_template('upload.html')


if __name__ == '__main__':
    app.run()

