from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class AddMesageForm(FlaskForm):
    text = TextAreaField("Текст:", validators=[DataRequired()])
    submit = SubmitField('Добавить')


class EditMesageForm(FlaskForm):
    text = TextAreaField("Изменение комментария:", validators=[DataRequired()])
    submit = SubmitField('Изменить')
