import datetime
import sqlalchemy
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin

from .users import User


class Message(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'massage'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_name = sqlalchemy.Column(sqlalchemy.String(length=100), autoincrement=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True)

    item_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("items.id"))
    item = orm.relation('Items')

    text = sqlalchemy.Column(sqlalchemy.String(length=1000), nullable=True)

    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
