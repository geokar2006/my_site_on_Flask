from flask import jsonify
from flask_restful import Resource, abort, reqparse
from data import db_session
from data.items import Items
from APIs.RestfulProtect import *


def abort_if_item_not_found(id):
    session = db_session.create_session()
    items = session.query(Items).get(id)
    if not items:
        abort(404, message=f"Item {id} not found")


class ItemResource(Resource):
    @api_auth.login_required
    def get(self, id):
        abort_if_item_not_found(id)
        session = db_session.create_session()
        items = session.query(Items).get(id)
        return jsonify({'items': items.to_dict(
            only=('title', 'content', 'user_id', 'is_private'))})

    @api_auth.login_required
    def delete(self, id):
        abort_if_item_not_found(id)
        session = db_session.create_session()
        news = session.query(Items).get(id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})


class ItemsListResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('title', required=True)
    parser.add_argument('content', required=True)
    parser.add_argument('is_private', required=True, type=bool)
    parser.add_argument('need_upload', required=True, type=bool)
    parser.add_argument('is_file', required=True, type=bool)
    parser.add_argument('file_link', required=True, type=str)
    parser.add_argument('uploaded_file_link', required=True, type=str)
    parser.add_argument('created_date', required=True, type=str)
    parser.add_argument('user_id', required=True, type=int)

    @api_auth.login_required
    def get(self):
        session = db_session.create_session()
        items = session.query(Items).all()
        return jsonify({'items': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in items]})

    @api_auth.login_required
    def post(self):
        args = self.parser.parse_args()
        session = db_session.create_session()
        items = Items(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            is_published=args['is_published'],
            is_private=args['is_private']
        )
        session.add(items)
        session.commit()
        return jsonify({'success': 'OK'})
