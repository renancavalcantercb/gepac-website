from werkzeug.security import generate_password_hash

from application import app, db
from flask import render_template, request, redirect, url_for, flash


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/news')
def news():
    return render_template('news.html')


@app.route('/semanadafisica')
def first_event():
    return render_template('semanadafisica.html')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        error = None

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

        user = db.users.find_one({'email': email})
        if user is not None:
            error = f'User {email} is already registered.'
            flash(error, category='danger')
            return render_template('semanadafisica.html')

        if password != confirm_password:
            error = 'Passwords do not match.'
            flash(error, category='danger')
            return render_template('semanadafisica.html')

        if error is None:
            try:
                db.users.insert_one({'email': email, 'password': generate_password_hash(password)})
            except Exception as e:
                error = f"Error occured: {e}"
                flash(error)
            else:
                flash(f'User {email} was successfully registered!', category='success')
                return redirect(url_for('first_event'))


@app.route('/login')
def login():
    return render_template('login.html')
