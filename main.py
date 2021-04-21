import json
import random
from flask_babel import Babel, _
from flask import Flask, render_template, redirect, request, abort
from dotenv import load_dotenv
from flask_restful import abort, Api
from werkzeug.utils import secure_filename
from wtforms import Label
from APIs.Gdrive import *
from APIs.items import ItemsListResource, ItemResource
from data import db_session
from data.items import Items
from data.message import Message
from data.users import User
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


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['ru', 'en'])


@app.route("/page/<int:id>/remove_message/<int:mes_id>", methods=['GET', 'POST'])
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
            form.text.label = Label(form.text.id, _("Изменение комментария:"))
            form.submit.label = Label(form.submit.id, _('Изменить'))
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
    form = AddMesageForm()
    if request.method == "GET":
        form.text.label = Label(form.text.id, _("Текст:"))
        form.submit.label = Label(form.submit.id, _('Добавить'))
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
                return render_template("page.html", items=items, item=item, form=form, title=item.title)
            else:
                abort(404)
    return render_template("page.html", items=items, item=item, form=form, title=item.title)


@app.route("/user/<int:id>", methods=['GET', 'POST'])
def user_page(id):
    if current_user.is_authenticated and id == current_user.id:
        return redirect("/me", 302)
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if current_user.is_authenticated and current_user.is_admin:
        form = AdminEditForm()
        if request.method == "GET":
            form.about.label = Label(form.about.id, _("О себе"))
            form.is_admin.label = Label(form.is_admin.id, _("Администратор"))
            form.is_approved.label = Label(form.is_approved.id, _('Одобрен'))
            form.submit.label = Label(form.submit.id, _('Изменить данные'))
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
        return render_template("user.html", user=user, form=form, title=user.name)
    return render_template("user.html", user=user, title=user.name)


@app.route("/me", methods=['GET', 'POST'])
@login_required
def current_user_page():
    db_sess = db_session.create_session()
    meid = current_user.id
    user = db_sess.query(User).filter(User.id == meid).first()
    form = MeEditForm()
    if request.method == "GET":
        form.about.label = Label(form.about.id, _("О вас"))
        form.password.label = Label(form.password.id, _('Пароль'))
        form.password_again.label = Label(form.password_again.id, _('Повторите пароль'))
        form.submit.label = Label(form.submit.id, _('Изменить данные'))
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
    if request.method == "GET":
        form.email.label = Label(form.email.id, _('Почта'))
        form.password.label = Label(form.password.id, _('Пароль'))
        form.password_again.label = Label(form.password_again.id, _('Повторите пароль'))
        form.name.label = Label(form.name.id, _('Имя пользователя'))
        form.about.label = Label(form.about.id, _("Немного о себе"))
        form.submit.label = Label(form.submit.id, _('Зарегистрироваться'))
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
def login():
    form = LoginForm()
    if request.method == "GET":
        form.email.label = Label(form.email.id, _('Почта'))
        form.password.label = Label(form.password.id, _('Пароль'))
        form.remember_me.label = Label(form.remember_me.id, _('Запомнить меня'))
        form.submit.label = Label(form.submit.id, _('Войти'))
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message=_("Неправильный логин или пароль"),
                               form=form)
    return render_template('login.html', title=_('Авторизация'), form=form)


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
        if request.method == "GET":
            form.title.label = Label(form.title.id, _('Заголовок'))
            form.content.label = Label(form.content.id, _('Содержание'))
            form.is_private.label = Label(form.is_private.id, _('Приватное'))
            form.need_upload.label = Label(form.need_upload.id, _('Нужно загружать файл?'))
            form.is_file.label = Label(form.is_file.id, _('Файл (поставьте галочку, если хотите прикрепить файл)'))
            form.file_link.label = Label(form.file_link.id, _('Ссылка'))
            form.uploaded_file.label = Label(form.uploaded_file.id, _('Файл'))
            form.submit.label = Label(form.submit.id, _('Создать'))
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
            elif not form.need_upload.data:
                item.file_link = form.file_link.data
            elif form.uploaded.data:
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
        return redirect("/", 302)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/item/<int:id>', methods=['GET', 'POST'])
@login_required
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
                form.submit.label = Label(form.submit.id, _("Изменить"))
            else:
                abort(404)
        if request.method == "POST":
            db_sess = db_session.create_session()
            item = db_sess.query(Items).filter(Items.id == id,
                                               Items.user == current_user
                                               ).first()
            if item:
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
                    db_sess.commit()
                    return thread_id
                elif not form.need_upload.data:
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


def main():
    global drive
    drive = DRIVEgetAPI(os.path.join(app.root_path, "creds.json"))
    api.add_resource(ItemsListResource, '/api/v2/items')
    api.add_resource(ItemResource, '/api/v2/item/<int:id>')
    db_session.global_init(os.path.join(app.root_path, 'db/site_data.db'))
    app.run(host='127.0.0.1', port=8080)


if __name__ == '__main__':
    main()
