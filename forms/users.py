from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Зарегистрироваться')


class AdminEditForm(FlaskForm):
    about = TextAreaField("О себе")
    is_admin = BooleanField("Администратор")
    is_approved = BooleanField('Одобрен')
    submit = SubmitField('Изменить данные')


class MeEditForm(FlaskForm):
    about = TextAreaField("О вас")
    password = PasswordField('Пароль')
    password_again = PasswordField('Повторите пароль')
    submit = SubmitField('Изменить данные')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
