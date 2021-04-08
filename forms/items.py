from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired


class ItemsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Приватное")
    need_upload = BooleanField("Нужно загружать файл?")
    is_file = BooleanField("Файл (иначе ссылка)")
    file_link = StringField('Ссылка')
    uploaded_file_link = FileField("Файл")
    submit = SubmitField('Создать')
