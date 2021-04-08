from flask import Flask, render_template, redirect, request, make_response, session, abort, send_from_directory, \
    send_file, url_for
from dotenv import load_dotenv
import os

from wtforms import Label

from data import db_session
from data.items import Items
from data.users import User
from forms.items import ItemsForm
from forms.users import RegisterForm, LoginForm, AdminEditForm, MeEditForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('KEY')
login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/page/<int:id>")
def item_page(id):
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        item = db_sess.query(Items).filter(
            ((Items.user == current_user) | (Items.is_private != True)) & (Items.id == id)).first()
        items = db_sess.query(Items).filter(
            (Items.user == current_user) | (Items.is_private != True))
    else:
        item = db_sess.query(Items).filter((Items.is_private != True) & (Items.id == id)).first()
        items = db_sess.query(Items).filter(Items.is_private != True)
    return render_template("page.html", items=items, item=item)


@app.route("/user/<int:id>", methods=['GET', 'POST'])
def user_page(id):
    if current_user.is_authenticated and id == current_user.id:
        return redirect("/me", 302)
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if current_user.is_authenticated and current_user.is_admin:
        form = AdminEditForm()
        if request.method == "GET":
            if form:
                form.is_admin.data = user.is_admin
                form.is_approved.data = user.is_approved
                form.about.data = user.about
            else:
                abort(404)
        if form.validate_on_submit():
            if user:
                user.is_admin = form.is_admin.data
                user.is_approved = form.is_approved.data
                user.about = form.about.data
                db_sess.commit()
                return redirect('/')
            else:
                abort(404)
        return render_template("user.html", user=user, form=form)
    return render_template("user.html", user=user)


@app.route("/me", methods=['GET', 'POST'])
@login_required
def current_user_page():
    db_sess = db_session.create_session()
    meid = current_user.id
    user = db_sess.query(User).filter(User.id == meid).first()
    form = MeEditForm()
    if request.method == "GET":
        if form:
            form.about.data = user.about
        else:
            abort(404)
    if form.validate_on_submit():
        if user:
            user.about = form.about.data
            if form.password.data != "" and form.password_again.data != "":
                user.set_password(form.password.data)
            db_sess.commit()
            return redirect('/me')
        else:
            abort(404)
    return render_template("me_user.html", user=user, form=form)


@app.route("/file/<path:link>")
def file(link):
    try:
        if "uploaded" in link:
            return send_file(link, as_attachment=True)
        else:
            return redirect("/", 302)
    except Exception:
        return redirect("/", 302)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        items = db_sess.query(Items).filter(
            (Items.user == current_user) | (Items.is_private != True))
    else:
        items = db_sess.query(Items).filter(Items.is_private != True)
    return render_template("index.html", items=items)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/new_item', methods=['GET', 'POST'])
@login_required
def add_item():
    if current_user.is_admin or current_user.is_approved:
        form = ItemsForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            items = Items()
            items.title = form.title.data
            items.content = form.content.data
            items.user = current_user
            items.need_upload = form.need_upload.data
            items.is_file = form.is_file.data
            items.is_private = form.is_private.data
            if not form.need_upload.data and form.is_file.data:
                f = form.uploaded_file_link.data
                filename = f.filename
                f.save(os.path.join(
                    app.root_path, 'uploaded', filename
                ))
                items.uploaded_file_link = f"/file/uploaded/{filename}"
            elif not form.need_upload.data:
                items.file_link = form.file_link.data
            current_user.items.append(items)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
        return render_template('add_item.html', title='Добавление записи',
                               form=form)
    else:
        return redirect("/", 302)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init('db/site_data.db')
    app.run(host='127.0.0.1', port=8080)


@app.route('/item/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    form = ItemsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        if current_user.is_admin:
            item = db_sess.query(Items).filter(Items.id == id).first()
        else:
            item = db_sess.query(Items).filter(Items.id == id, Items.user == current_user).first()
        if item:
            form.title.data = item.title
            form.content.data = item.content
            form.is_private.data = item.is_private
            form.is_file.data = item.is_file
            form.submit.label = Label(form.submit.id, "Изменить")
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        item = db_sess.query(Items).filter(Items.id == id,
                                           Items.user == current_user
                                           ).first()
        if item:
            item.title = form.title.data
            item.content = form.content.data
            item.is_private = form.is_private.data
            item.need_upload = form.need_upload.data
            item.is_file = form.is_file.data
            if not form.need_upload.data and form.is_file.data:
                f = form.uploaded_file_link.data
                print(f)
                filename = f.filename
                f.save(os.path.join(
                    app.root_path, 'uploaded', filename
                ))
                item.uploaded_file_link = f"/file/uploaded/{filename}"
            elif not form.need_upload.data:
                item.file_link = form.file_link
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_item.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/item_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def item_delete(id):
    db_sess = db_session.create_session()
    item = db_sess.query(Items).filter(Items.id == id,
                                       Items.user == current_user
                                       ).first()
    if item:
        db_sess.delete(item)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


if __name__ == '__main__':
    main()
