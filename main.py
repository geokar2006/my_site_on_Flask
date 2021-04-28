import functools
import json
import random
from flask_babel import Babel, _
from flask import Flask, render_template, redirect, request, abort, jsonify
from dotenv import load_dotenv
from flask_restful import abort, Api
from werkzeug.utils import secure_filename
from wtforms import Label
from APIs.Gdrive import *
from APIs.items import ItemsListResource, ItemResource
from data import db_session
from data.items import Items
from data.message import Message
from data.site_settings import site_settings
from data.users import User
from forms.admin_panel import Admin_Panel_Form
from forms.items import ItemsForm
from forms.message import AddMesageForm, EditMesageForm
from forms.users import RegisterForm, LoginForm, AdminEditForm, MeEditForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

load_dotenv()

app = Flask(__name__)
api = Api(app)

babel = Babel(app)
app.config['SECRET_KEY'] = os.getenv('KEY')
login_manager = LoginManager()
login_manager.init_app(app)

drive = None

inited = False


def debugmode(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        db_sess = db_session.create_session()
        if db_sess:
            settings = db_sess.query(site_settings).filter(site_settings.id == 1).first()
            if (settings.debug_mode and (
                    current_user.is_authenticated and (
                    current_user.is_admin or current_user.is_approved))) \
                    or not settings.debug_mode:
                return f(*args, **kwargs)
            else:
                return redirect("/debug", 302)

    return decorated_function


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['ru', 'en'])


@app.route("/page/<int:id>/remove_message/<int:mes_id>", methods=['GET', 'POST'])
@login_required
@debugmode
def remove_message(id, mes_id):
    db_sess = db_session.create_session()
    mesage = db_sess.query(Message).filter(Message.item_id == id, Message.id == mes_id).first()
    if current_user.is_authenticated and (current_user.id == mesage.id or current_user.is_admin):
        if mesage:
            db_sess.delete(mesage)
            db_sess.commit()
        return redirect(f'/page/{id}', 302)
    else:
        abort(404)
    return redirect(f'/page/{id}', 302)


@app.route("/check_file_uploaded/<sec_name>", methods=['GET', 'POST'])
def file_cheker(sec_name):
    return str(check_if_file_exist(drive, sec_name))


@app.route("/page/<int:id>/message/<int:mes_id>", methods=['GET', 'POST'])
@login_required
@debugmode
def edit_message(id, mes_id):
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        item = db_sess.query(Items).filter(
            ((Items.user == current_user) | (Items.is_private != True)) & (Items.id == id)).first()
        items = db_sess.query(Items).filter(
            (Items.user == current_user) | (Items.is_private != True))
    else:
        item = db_sess.query(Items).filter((Items.is_private != True) & (Items.id == id)).first()
        items = db_sess.query(Items).filter(Items.is_private != True)
    if current_user.is_authenticated:
        form = EditMesageForm()
        if request.method == "GET":
            if form:
                form.text.data = item.messages[mes_id].text
            else:
                abort(404)
        if form.validate_on_submit():
            if item:
                item.messages[mes_id].text = form.text.data
                db_sess.commit()
                return redirect(f"/page/{id}", 302)
            else:
                abort(404)
        return render_template("page.html", items=items, item=item, form=form, title=item.title)
    return redirect(f"/page/{id}", 302)


def is_dict(dict, key):
    try:
        dict[key]
        return True
    except KeyError:
        return False


@app.route("/page_download", methods=['POST'])
def page_download():
    global exporting_threads
    if request.method == "POST":
        name = request.form['filename']
        if check_if_file_exist(drive, name):
            file_list = drive.files().list(q=f"'{os.getenv('GAPI_FOLDER_ID')}' in parents", supportsAllDrives=True,
                                           includeItemsFromAllDrives=True).execute()['files']
            idd, type = -1, ""
            for i in file_list:
                if i['name'] == name:
                    idd = i['id']
                    type = str(i['mimeType']).split("/")[-1]
            thread_id = None
            while True:
                thread_id = str(random.randint(0, 100000))
                if not is_dict(exporting_threads, thread_id):
                    break
            exporting_threads[thread_id] = Downloader(idd, name, type, drive, app, thread_id)
            exporting_threads[thread_id].start()
            return json.dumps({'success': 'true', 'id': int(thread_id)})


@app.route("/page/<int:id>", methods=['GET', 'POST'])
@debugmode
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
    if item:
        form = AddMesageForm()
        if request.method == "POST":
            if current_user.is_authenticated and form.validate_on_submit():
                if item:
                    message = Message()
                    message.item = item
                    message.item_id = item.id
                    message.user_id = current_user.id
                    message.user_name = current_user.name
                    message.text = form.text.data
                    item.messages.append(message)
                    db_sess.commit()
                else:
                    abort(404)
        return render_template("page.html", items=items, item=item, form=form, title=item.title)
    return abort(404)


@app.route("/user/<int:id>", methods=['GET', 'POST'])
@debugmode
def user_page(id):
    if current_user.is_authenticated and id == current_user.id:
        return redirect("/me", 302)
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if user:
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
            return render_template("user.html", form=form, user=user, title=user.name)
        return render_template("user.html", user=user, title=user.name)
    else:
        abort(404)


@app.errorhandler(404)
@debugmode
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/me", methods=['GET', 'POST'])
@login_required
@debugmode
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
    return render_template("me_user.html", user=user, form=form, title="Вы")


@app.route("/")
@debugmode
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        items = db_sess.query(Items).filter(
            (Items.user == current_user) | (Items.is_private != True))
    else:
        items = db_sess.query(Items).filter(Items.is_private != True)
    return render_template("index.html", items=items)


@app.route('/register', methods=['GET', 'POST'])
@debugmode
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title=_('Регистрация'),
                                   form=form,
                                   message=_("Пароли не совпадают"))
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title=_('Регистрация'),
                                   form=form,
                                   message=_("Такой пользователь уже есть"))
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title=_('Регистрация'), form=form)


@app.route('/login', methods=['GET', 'POST'])
@debugmode
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
    return render_template('login.html', title=_('Авторизация'), form=form)


@app.route('/logout')
@login_required
@debugmode
def logout():
    logout_user()
    return redirect("/")


@app.route('/new_item', methods=['GET', 'POST'])
@login_required
@debugmode
def add_item():
    if current_user.is_admin or current_user.is_approved:
        form = ItemsForm()
        if request.method == "POST":
            db_sess = db_session.create_session()
            db_sess.expire_on_commit = False
            item = Items()
            item.title = form.title.data
            item.content = form.content.data
            item.user = current_user
            item.need_upload = form.need_upload.data
            item.is_file = form.is_file.data
            item.is_private = form.is_private.data
            if form.need_upload.data and form.is_file.data and not form.uploaded.data:
                filename = form.uploaded_file.data.filename
                sfilename = secure_filename(filename)
                thread_id = None
                while True:
                    thread_id = str(random.randint(0, 100000))
                    if not is_dict(exporting_threads, thread_id):
                        break
                exporting_threads[thread_id] = Uploader(sfilename, form.uploaded_file.data.stream.read(),
                                                        form.uploaded_file.data.stream.tell(), drive, app)
                exporting_threads[thread_id].start()
                form.uploaded_file.data.stream.close()
                item.uploaded_file_secured_name = sfilename
                item.uploaded_file_name = filename
                current_user.items.append(item)
                db_sess.merge(current_user)
                db_sess.commit()
                return thread_id
            elif form.need_upload.data and not form.is_file.data:
                item.file_link = form.file_link.data
            elif form.need_upload.data:
                filename = form.uploaded_filename.data
                sfilename = secure_filename(filename)
                item.uploaded_file_secured_name = sfilename
                item.uploaded_file_name = filename
            current_user.items.append(item)
            db_sess.merge(current_user)
            db_sess.commit()
        return render_template('add_item.html', title=_('Добавление записи'),
                               form=form)
    else:
        abort(404)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/item/<int:id>', methods=['GET', 'POST'])
@login_required
@debugmode
def edit_item(id):
    if current_user.is_admin or current_user.is_approved:
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
                form.need_upload.data = item.need_upload
                form.is_private.data = item.is_private
                form.is_file.data = item.is_file
                form.file_link.data = item.file_link
            else:
                abort(404)
        if request.method == "POST":
            db_sess = db_session.create_session()
            if current_user.is_admin:
                item = db_sess.query(Items).filter(Items.id == id).first()
            else:
                item = db_sess.query(Items).filter(Items.id == id, Items.user == current_user).first()
            if item:
                item.title = form.title.data
                item.content = form.content.data
                item.need_upload = form.need_upload.data
                item.is_file = form.is_file.data
                item.is_private = form.is_private.data
                if form.need_upload.data and form.is_file.data and not form.uploaded.data:
                    filename = form.uploaded_file.data.filename
                    sfilename = secure_filename(filename)
                    thread_id = None
                    while True:
                        thread_id = str(random.randint(0, 100000))
                        if not is_dict(exporting_threads, thread_id):
                            break
                    exporting_threads[thread_id] = Uploader(sfilename, form.uploaded_file.data.stream.read(),
                                                            form.uploaded_file.data.stream.tell(), drive, app)
                    exporting_threads[thread_id].start()
                    form.uploaded_file.data.stream.close()
                    item.uploaded_file_secured_name = sfilename
                    item.uploaded_file_name = filename
                    db_sess.commit()
                    return thread_id
                elif form.need_upload.data and not form.is_file.data:
                    item.file_link = form.file_link.data
                elif form.uploaded.data:
                    filename = form.uploaded_filename.data
                    sfilename = secure_filename(filename)
                    item.uploaded_file_secured_name = sfilename
                    item.uploaded_file_name = filename
                db_sess.commit()
                return redirect('/')
            else:
                abort(404)
        return render_template('add_item.html',
                               title=_('Редактирование записи'),
                               form=form
                               )


@app.route('/item_delete/<int:id>', methods=['GET', 'POST'])
@login_required
@debugmode
def item_delete(id):
    db_sess = db_session.create_session()
    if current_user.is_admin:
        item = db_sess.query(Items).filter(Items.id == id).first()
    else:
        item = db_sess.query(Items).filter(Items.id == id,
                                           Items.user == current_user
                                           ).first()
    if item:
        file_list = drive.files().list(q=f"'{os.getenv('GAPI_FOLDER_ID')}' in parents", supportsAllDrives=True,
                                       includeItemsFromAllDrives=True).execute()['files']
        for i in file_list:
            if i['name'] == item.uploaded_file_secured_name:
                drive.files().delete(fileId=i['id'], supportsAllDrives=True, supportsTeamDrives=True).execute()
        db_sess.delete(item)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/progress/<int:thread_id>')
def progress(thread_id):
    global exporting_threads

    return str(exporting_threads[str(thread_id)].progress)


@app.route('/finish_progress/<int:thread_id>')
def finish_progress(thread_id):
    global exporting_threads
    resp = exporting_threads[str(thread_id)].resp
    exporting_threads.pop(str(thread_id))
    return resp


@app.route('/admin_panel', methods=['GET', 'POST'])
@login_required
@debugmode
def adminka():
    if not current_user.is_admin:
        abort(404)
    form = Admin_Panel_Form()
    db_sess = db_session.create_session()
    settings = db_sess.query(site_settings).filter(site_settings.id == 1).first()
    if request.method == "GET":
        form.debug_mode.data = settings.debug_mode
        form.message.data = settings.debug_message
        form.redirect_link.data = settings.debug_redirect_page
    if form.submit.data:
        settings.debug_mode = form.debug_mode.data
        settings.debug_message = form.message.data
        settings.debug_redirect_page = form.redirect_link.data
        db_sess.commit()
    return render_template("adminpage.html", title=_('Админ-панель'), form=form)


@app.route("/debug")
def debugmes():
    db_sess = db_session.create_session()
    settings = db_sess.query(site_settings).filter(site_settings.id == 1).first()
    return render_template("debug.html", settings=settings, title=_("Ведуться технические работы"))


def main():
    global drive, inited
    drive = DRIVEgetAPI(os.path.join(app.root_path, "creds.json"))
    api.add_resource(ItemsListResource, '/api/v2/items')
    api.add_resource(ItemResource, '/api/v2/item/<int:id>')
    db_session.global_init(f"sqlite:///{os.path.join(app.root_path, 'db/site_data.db')}?check_same_thread=False")
    app.run(host='127.0.0.1', port=8080)
    inited = True


if __name__ == '__main__':
    main()
