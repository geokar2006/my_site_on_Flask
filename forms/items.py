from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired


class ItemsForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    content = TextAreaField()
    is_private = BooleanField()
    uploaded = BooleanField()
    uploaded_filename = StringField()
    need_upload = BooleanField()
    is_file = BooleanField()
    file_link = StringField()
    uploaded_file = FileField()
    submit = SubmitField()
