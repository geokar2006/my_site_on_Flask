from flask_wtf import FlaskForm
from flask_babel import _
from wtforms import TextAreaField, SubmitField, Label
from wtforms.validators import DataRequired


class AddMesageForm(FlaskForm):
    text = TextAreaField(validators=[DataRequired()])
    submit = SubmitField()

    def __init__(self):
        super().__init__()
        self.text.label = Label(self.text.id, _("Текст:"))
        self.submit.label = Label(self.submit.id, _('Добавить'))


class EditMesageForm(FlaskForm):
    text = TextAreaField(validators=[DataRequired()])
    submit = SubmitField()

    def __init__(self):
        super().__init__()
        self.text.label = Label(self.text.id, _("Изменение комментария:"))
        self.submit.label = Label(self.submit.id, _('Изменить'))
