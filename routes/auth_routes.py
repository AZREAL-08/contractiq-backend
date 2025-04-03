from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from firebase_admin import auth
from services.firebase_service import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']

        try:
            user = auth.create_user(email=email, password=password)
            session['user_email'] = email
            # Save user to Firestore
            db.collection('users').document(user.uid).set({
                'email': email,
                'uid': user.uid,
                'name': name
            })
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f"Registration failed: {e}", "danger")
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        try:
            user = auth.get_user_by_email(email)
            name = db.collection('users').document(user.uid).get().get('name')
            session['user_id'] = user.uid
            session['user_email'] = email
            session['name'] = name
            return redirect(url_for('dashboard.dashboard'))
        except Exception as e:
            flash(f"Login failed: {e}", "danger")
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
