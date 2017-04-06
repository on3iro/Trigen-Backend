from flask_restful import Resource
from app import db
from triserv import abort_if_not_allowed, parser, bcrypt
from models import user
from flask_jwt import jwt_required
import random


class User(Resource):
    def generate_user_hash(self):
        uhash = random.getrandbits(128)
        return "%032x" % uhash

    @jwt_required()
    def get(self, user_id):
        abort_if_not_allowed(user_id)

        dbuser = user.User.query.filter_by(id=int(user_id)).first()

        retuser = {
            'email': dbuser.email,
            'hash': dbuser.userhash,
            'slots': dbuser.slots,
        }
        return retuser

    def post(self):
        args = parser.parse_args()
        pw_hash = bcrypt.generate_password_hash(
            args['password']).decode('utf-8')

        new_user = user.User(args['email'], pw_hash)
        new_user.slots = 5  # TODO: do it the right way
        new_user.userhash = self.generate_user_hash()
        db.session.add(new_user)
        db.session.commit()
        retuser = {
            'id': new_user.id,
            'email': new_user.email,
        }
        return retuser

    @jwt_required()
    def delete(self, user_id):
        # TODO: implement
        pass

    @jwt_required()
    def put(self, user_id):
        if 1:
            return {'message': 'Action not supported'}
        dbuser = user.User.query.filter_by(id=int(user_id)).first()
        args = parser.parse_args()
        # TODO: Check old password

        dbuser.email = args['email']
        dbuser.password = args['newpassword']

        db.session.add(dbuser)
        db.session.commit()
        return {
            'id': dbuser.id,
            'email': dbuser.email,
            'password': dbuser.password}

    class UserHash(Resource):
        @jwt_required()
        def get(self, user_id):
            abort_if_not_allowed(user_id)
            dbuser = user.User.query.filter_by(id=int(user_id)).first()
            retjson = {
                'hash': dbuser.userhash
            }
            return retjson
