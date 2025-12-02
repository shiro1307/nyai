from flask import render_template, request, redirect, url_for, session, flash
from functools import wraps
import database

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

def register_auth_routes(app):
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            confirm = request.form.get('confirm_password')
            
            if password != confirm:
                flash('Passwords do not match')
                return render_template('signup.html')
            
            if database.create_user(username, password):
                flash('Account created! Please login.')
                return redirect(url_for('login'))
            else:
                flash('Username already exists')
                return render_template('signup.html')
        
        return render_template('signup.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = database.get_user(username)
            
            if user and database.verify_password(user, password):
                session['user_id'] = user.doc_id
                session['username'] = username
                flash('Login successful!')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password')
        
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Logged out successfully')
        return redirect(url_for('login'))