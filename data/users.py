import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(length=100), nullable=True, unique=True)
    about = sqlalchemy.Column(sqlalchemy.String(length=1000), nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String(length=100),
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String(length=2000), nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    items = orm.relation("Items", back_populates='user', lazy='subquery')

    is_admin = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    is_approved = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    def __repr__(self):
        return f'Имя пользователя: {self.name}\tО себе: {self.about}\tЭл. почта: {self.email}\tДата и время регистрации: {self.created_date}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
