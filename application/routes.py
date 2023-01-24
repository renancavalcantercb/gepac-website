from pymongo import DESCENDING
from werkzeug.security import generate_password_hash, check_password_hash
from .utils import utils
from application import app, db, posts
from flask import render_template, request, redirect, url_for, flash, g, session
from datetime import datetime
from bson import ObjectId


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/news')
def news():
    # search for all news in posts collection
    news = posts.find().sort("date_posted", DESCENDING)
    return render_template('news.html', news=news)


@app.route('/add-news', methods=['GET', 'POST'])
def add_news():
    if request.method == 'POST':
        id = utils.generate_id()
        title = request.form['title']
        resume = request.form['resume']
        content = request.form['content']
        img_url = request.form['img_url']
        slug = utils.slugify(title)
        author = request.form['author']
        date_posted = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if title and content and author and date_posted:
            if db.news.find_one({'slug': slug}) or db.news.find_one({'title': title}):
                flash('Title or slug already exists')
                return redirect(url_for('add_news'))

            db.posts.insert_one({
                '_id': id,
                'title': title,
                'resume': resume,
                'content': content,
                'img_url': img_url,
                'author': author,
                'date_posted': date_posted
            })
            return redirect(url_for('news'))

        flash('Please fill all fields')
        return redirect(url_for('add_news'))
    return render_template('add-news.html')


@app.route('/semanadafisica')
def first_event():
    return render_template('semanadafisica.html')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        admin = False
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
                db.users.insert_one({'email': email, 'password': generate_password_hash(password), 'admin': admin})
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
                session['logged_in'] = True
                session['email'] = email
                session['admin'] = user['admin']
                return redirect(url_for('index'))

            else:
                error = 'Incorrect password.'
                flash(error, category='danger')
                return render_template('login.html')


@app.route('/user/admin')
@utils.login_required
@utils.is_admin
def admin():
    if session['admin']:
        users = db.users.find()
        users_with_roles = []
        for user in users:
            user['admin'] = 'Admin' if user['admin'] else 'User'
            users_with_roles.append(user)

        return render_template('admin.html', users=users_with_roles)


@app.route('/user/admin/<user_id>/edit', methods=['GET', 'POST'])
@utils.login_required
@utils.is_admin
def edit_user(user_id):
    if request.method == 'GET':
        user = db.users.find_one({'_id': ObjectId(user_id)})
        return render_template('user.html', user=user)

    elif request.method == 'POST':
        user = db.users.find_one({'_id': ObjectId(user_id)})

        if request.form['email'] != user['email']:
            user['email'] = request.form['email']

        if request.form.get('admin', False) != user['admin']:
            user['admin'] = request.form.get('admin', False)

        db.users.update_one({'_id': ObjectId(user_id)}, {'$set': user})
        return redirect(url_for('admin'))


@app.route('/user/admin/<user_id>/delete')
@utils.login_required
@utils.is_admin
def delete_user(user_id):
    db.users.delete_one({'_id': ObjectId(user_id)})
    return redirect(url_for('admin'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    session['email'] = None
    session.clear()
    return redirect(url_for('index'))
