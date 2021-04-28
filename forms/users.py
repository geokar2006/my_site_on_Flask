import re
from flask_wtf import FlaskForm
from flask_babel import _
from email_validator import validate_email, EmailNotValidError
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, Label
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, ValidationError, equal_to
from data import db_session
from data.users import User


def email_validator(form, email):
    try:
        validate_email(email.data, allow_smtputf8=False)
    except EmailNotValidError as e:
        raise ValidationError(str(e))
    db_sess = db_session.create_session()
    finded = db_sess.query(User).filter(User.email == email.data).first()
    if finded:
        raise ValidationError(_("Данная почта уже использована"))


def password_validator(form, password):
    paswd = password.data
    if len(paswd) < 8:
        raise ValidationError(_("Минамальное колличество символов в пароле: 8"))
    elif re.search('[0-9]', paswd) is None:
        raise ValidationError(_("Пароль должен иметь цифры"))
    elif re.search('[A-Z]', paswd) is None:
        raise ValidationError(_("Пароль должен иметь заглавные буквы"))
    elif ' ' in paswd:
        raise ValidationError(_("Пароль НЕ должен иметь пробелы"))


def user_name_check(form, user):
    db_sess = db_session.create_session()
    finded = db_sess.query(User).filter(User.name == user.data).first()
    if finded:
        raise ValidationError(_("Имя пользывателя занято"))


class RegisterForm(FlaskForm):
    email = EmailField(validators=[DataRequired(), email_validator])
    password = PasswordField(validators=[DataRequired(), password_validator])
    password_again = PasswordField(validators=[DataRequired(), equal_to('password_again')])
    name = StringField(validators=[DataRequired(), user_name_check])
    about = TextAreaField()
    submit = SubmitField()

    def __init__(self):
        super().__init__()
        self.email.label = Label(self.email.id, _('Почта'))
        self.password.label = Label(self.password.id, _('Пароль'))
        self.password_again.label = Label(self.password_again.id, _('Повторите пароль'))
        self.name.label = Label(self.name.id, _('Имя пользователя'))
        self.about.label = Label(self.about.id, _("Немного о себе"))
        self.submit.label = Label(self.submit.id, _('Зарегистрироваться'))


class AdminEditForm(FlaskForm):
    about = TextAreaField()
    is_admin = BooleanField()
    is_approved = BooleanField()
    submit = SubmitField()

    def __init__(self):
        super().__init__()
        self.about.label = Label(self.about.id, _("О себе"))
        self.is_admin.label = Label(self.is_admin.id, _("Администратор"))
        self.is_approved.label = Label(self.is_approved.id, _('Одобрен'))
        self.submit.label = Label(self.submit.id, _('Изменить данные'))


class MeEditForm(FlaskForm):
    about = TextAreaField()
    password = PasswordField()
    password_again = PasswordField()
    submit = SubmitField()

    def __init__(self):
        super().__init__()
        self.about.label = Label(self.about.id, _("О вас"))
        self.password.label = Label(self.password.id, _('Пароль'))
        self.password_again.label = Label(self.password_again.id, _('Повторите пароль'))
        self.submit.label = Label(self.submit.id, _('Изменить данные'))


class LoginForm(FlaskForm):
    email = EmailField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    remember_me = BooleanField()
    submit = SubmitField()

    def __init__(self):
        super().__init__()
        self.email.label = Label(self.email.id, _('Почта'))
        self.password.label = Label(self.password.id, _('Пароль'))
        self.remember_me.label = Label(self.remember_me.id, _('Запомнить меня'))
        self.submit.label = Label(self.submit.id, _('Войти'))
