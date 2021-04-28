from flask_wtf import FlaskForm
from flask_babel import _
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, Label
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    password_again = PasswordField(validators=[DataRequired()])
    name = StringField(validators=[DataRequired()])
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
