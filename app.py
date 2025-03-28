from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
import extract
from process import process_file_content


app = Flask(__name__)
app.secret_key = 'ac5ab744684a0585c7bde4a3285057468440df322d09c61f6986621d62301f3f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)


# Initialize the database
with app.app_context():
    db.create_all()


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
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another.', 'error')
            return redirect(url_for('register'))

        # Hash password and save to database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        # Authenticate User
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['username'] = username
            if remember:
                session.permanent = True
            flash('Login successful!', 'success')
            return redirect(url_for('upload'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


# Logout Route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # Check if user is logged in
    username = session.get('username')
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
        return jsonify({"extracted_data": extracted_contents})

    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)

