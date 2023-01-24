from werkzeug.security import generate_password_hash, check_password_hash
from .utils import utils
from application import app, db
from flask import render_template, request, redirect, url_for, flash, g, session


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
                db.session.insert_one({'email': email, 'password': generate_password_hash(password)})
            except Exception as e:
                error = f"Error occured: {e}"
                flash(error)
            else:
                flash(f'User {email} was successfully registered!', category='success')
                return redirect(url_for('first_event'))


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

        user = db.users.find_one({'email': email})
        if user is None:
            error = f'User {email} is not registered.'
            flash(error, category='danger')
            return render_template('login.html')

        if error is None:
            if check_password_hash(user['password'], password):
                flash(f'User {email} was successfully logged in!', category='success')
                session['logged_in'] = True
                session['email'] = email
                return redirect(url_for('index'))

            else:
                error = 'Incorrect password.'
                flash(error, category='danger')
                return render_template('login.html')


@app.route('/private')
@utils.login_required
def private():
    return "you are logged in!"


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    session['email'] = None
    session.clear()
    return redirect(url_for('index'))
