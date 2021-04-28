from flask_wtf import FlaskForm
from flask_babel import _
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, Label
from wtforms.validators import DataRequired


class Admin_Panel_Form(FlaskForm):
    debug_mode = BooleanField()
    message = TextAreaField(validators=[DataRequired()])
    redirect_link = StringField(validators=[DataRequired()])
    submit = SubmitField()

    def __init__(self):
        super().__init__()
        self.debug_mode.label = Label(self.debug_mode.id, _("Режим отладки"))
        self.message.label = Label(self.message.id, _("Сообщение"))
        self.redirect_link.label = Label(self.redirect_link.id, _("Страница для перенапровления"))
        self.submit.label = Label(self.submit.id, _("Изменить"))

