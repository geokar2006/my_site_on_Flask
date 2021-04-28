import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class site_settings(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'site_settings'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    debug_mode = sqlalchemy.Column(sqlalchemy.Boolean)

    debug_message = sqlalchemy.Column(sqlalchemy.String(length=1000))

    debug_redirect_page = sqlalchemy.Column(sqlalchemy.String(length=1000))
