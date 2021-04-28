from flask_wtf import FlaskForm
from flask_babel import _
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FileField, Label
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

    def __init__(self):
        super().__init__()
        self.title.label = Label(self.title.id, _('Заголовок'))
        self.content.label = Label(self.content.id, _('Содержание'))
        self.is_private.label = Label(self.is_private.id, _('Приватное'))
        self.need_upload.label = Label(self.need_upload.id, _('Нужно загружать файл?'))
        self.is_file.label = Label(self.is_file.id, _('Файл (поставьте галочку, если хотите прикрепить файл)'))
        self.file_link.label = Label(self.file_link.id, _('Ссылка'))
        self.uploaded_file.label = Label(self.uploaded_file.id, _('Файл'))
        self.submit.label = Label(self.submit.id, _("Изменить"))
