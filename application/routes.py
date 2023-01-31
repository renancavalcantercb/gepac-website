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
    news = posts.find().sort("date_posted", DESCENDING)
    return render_template('news.html', news=news)


@app.route('/news/<slug>')
def news_detail(slug):
    news = db.posts.find_one({'slug': slug})
    return render_template('news-detail.html', news=news)


@app.route('/semanadafisica')
def first_event():
    return render_template('semanadafisica.html')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        cpf = request.form['cpf']
        birthdate = request.form['birthdate']
        phone = request.form['phone']
        course = request.form['course']

        error = None
        flash_message = None
        flash_category = None

        if password != confirm_password:
            error = 'As senhas não conferem'

        if error is None:
            user_email = db.stundents.find_one({'email': email})
            if user_email is not None:
                error = f'O email {email} já está cadastrado.'
            else:
                user_cpf = db.stundents.find_one({'cpf': cpf})
                if user_cpf is not None:
                    error = f'O cpf {cpf} já está cadastrado.'
                else:
                    user_phone = db.stundents.find_one({'phone': phone})
                    if user_phone is not None:
                        error = f'O telefone {phone} já está cadastrado.'

        if error is None:
            try:
                db.stundents.insert_one(
                    {'name': name, 'email': email, 'password': generate_password_hash(password), 'cpf': cpf,
                     'birthdate': birthdate, 'phone': phone, 'course': course, 'admin': False})
                flash_message = f'Usuário {email} cadastrado com sucesso!'
                flash_category = 'success'
            except Exception as e:
                error = f"Error occured: {e}"

        if error:
            flash(error, category='danger')
        if flash_message:
            flash(flash_message, category=flash_category)

        return redirect(url_for('first_event' if flash_message else 'semanadafisica'))


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
            error = 'O Email é obrigatório.'
        elif not password:
            error = 'A senha é obrigatória.'

        user = db.users.find_one({'email': email})
        if user is None:
            error = f'{email} não cadastrado.'
            flash(error, category='danger')
            return render_template('login.html')

        if error is None:
            if check_password_hash(user['password'], password):
                session['logged_in'] = True
                session['name'] = user['name']
                session['admin'] = user['admin']
                return redirect(url_for('index'))

            else:
                error = 'Usuário ou senha incorretos.'
                flash(error, category='danger')
                return render_template('login.html')


@app.route('/user/admin')
@utils.login_required
@utils.is_admin
def admin():
    if session['admin']:
        users = db.users.find()
        stundents = db.stundents.find()
        posts = db.posts.find()
        users_with_roles = []
        students_courses = []
        course_map = {
            '1': 'Selenografia',
            '2': 'Física Estatística',
            '3': 'Python para física'
        }

        for user in users:
            user['admin'] = 'Admin' if user['admin'] else 'User'
            users_with_roles.append(user)

        for stundent in stundents:
            stundent['course'] = course_map.get(stundent['course'], 'Desconhecido')
            students_courses.append(stundent)

        return render_template('admin.html', users=users_with_roles, posts=list(posts), students=students_courses)


@app.route('/user/admin/create', methods=['POST'])
@utils.login_required
@utils.is_admin
def create_user():
    if session['admin']:
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']
        admin = True if role == 'admin' else False
        error = None

        if not email:
            error = 'Email is required.'
            return redirect(url_for('admin'))
        elif not password:
            error = 'Password is required.'
            return redirect(url_for('admin'))
        elif password != confirm_password:
            error = 'Passwords do not match.'
            return redirect(url_for('admin'))

        if error is None:
            try:
                db.users.insert_one({'email': email, 'password': generate_password_hash(password), 'admin': admin})
            except Exception as e:
                error = f"Error occured: {e}"
                flash(error)
            else:
                flash(f'User {email} was successfully registered!', category='success')
                return redirect(url_for('admin'))


@app.route('/user/admin/<user_id>/edit', methods=['GET', 'POST'])
@utils.login_required
@utils.is_admin
def edit_user(user_id):
    if request.method == 'POST':
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


@app.route('/add-news', methods=['GET', 'POST'])
@utils.login_required
@utils.is_admin
def add_news():
    if request.method == 'POST':
        id = utils.generate_id()
        title = request.form['title']
        resume = request.form['resume']
        content = utils.text_to_html(request.form['content'])
        img_url = request.form['img_url']
        slug = utils.slugify(title)
        author = request.form['author']
        date_posted = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if title and content and author and date_posted:
            if db.news.find_one({'slug': slug}) or db.news.find_one({'title': title}):
                flash('Title or slug already exists')
                return redirect(url_for('admin'))

            db.posts.insert_one({
                '_id': id,
                'title': title,
                'resume': resume,
                'slug': slug,
                'content': content,
                'img_url': img_url,
                'author': author,
                'date_posted': date_posted
            })
            return redirect(url_for('admin'))

        flash('Please fill all fields')
        return redirect(url_for('admin'))
    return redirect(url_for('admin'))


@app.route('/news/<post_id>/edit', methods=['GET', 'POST'])
@utils.login_required
@utils.is_admin
def edit_news(post_id):
    if request.method == 'POST':
        news = db.posts.find_one({'_id': post_id})
        if request.form['title'] != news['title']:
            news['title'] = request.form['title']
            news['slug'] = utils.slugify(request.form['title'])
        elif request.form['resume'] != news['resume']:
            news['resume'] = request.form['resume']
        elif request.form['content'] != news['content']:
            news['content'] = utils.text_to_html(request.form['content'])
        elif request.form['img_url'] != news['img_url']:
            news['img_url'] = request.form['img_url']
        elif request.form['author'] != news['author']:
            news['author'] = request.form['author']

        db.posts.update_one({'_id': post_id}, {'$set': news})
        return redirect(url_for('admin'))


@app.route('/news/<post_id>/delete')
@utils.login_required
@utils.is_admin
def delete_news(post_id):
    print(post_id)
    db.posts.delete_one({'_id': post_id})
    return redirect(url_for('admin'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    session['email'] = None
    session.clear()
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
