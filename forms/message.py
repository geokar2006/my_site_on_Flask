from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class AddMesageForm(FlaskForm):
    text = TextAreaField(validators=[DataRequired()])
    submit = SubmitField()


class EditMesageForm(FlaskForm):
    text = TextAreaField(validators=[DataRequired()])
    submit = SubmitField()
