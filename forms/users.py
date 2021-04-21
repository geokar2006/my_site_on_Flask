from flask_wtf import FlaskForm
from flask_babel import _
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    password_again = PasswordField(validators=[DataRequired()])
    name = StringField(validators=[DataRequired()])
    about = TextAreaField()
    submit = SubmitField()


class AdminEditForm(FlaskForm):
    about = TextAreaField()
    is_admin = BooleanField()
    is_approved = BooleanField()
    submit = SubmitField()


class MeEditForm(FlaskForm):
    about = TextAreaField()
    password = PasswordField()
    password_again = PasswordField()
    submit = SubmitField()


class LoginForm(FlaskForm):
    email = EmailField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    remember_me = BooleanField()
    submit = SubmitField()
    submit = SubmitField()
