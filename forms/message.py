from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

class AddMesageForm(FlaskForm):
    text = TextAreaField("Текст:", validators=[DataRequired()])
    submit = SubmitField('Добавить')
