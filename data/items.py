import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Items(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'items'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String(length=100), nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String(length=10000), nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User', lazy='subquery')

    need_upload = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    is_file = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    file_link = sqlalchemy.Column(sqlalchemy.String(length=100), nullable=True)

    uploaded_file_name = sqlalchemy.Column(sqlalchemy.String(length=100), nullable=True)

    uploaded_file_secured_name = sqlalchemy.Column(sqlalchemy.String(length=100), nullable=True)

    messages = orm.relation("Message", back_populates='item', lazy='subquery')
