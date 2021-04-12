from flask import make_response, jsonify
from flask_httpauth import HTTPBasicAuth
from data import db_session
from data.users import User

api_auth = HTTPBasicAuth()


@api_auth.verify_password
def verify_password(username, paswd):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == username).first()
    if user.is_admin and user.check_password(paswd):
        return username
    return None


@api_auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)
