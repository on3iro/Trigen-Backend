from __future__ import print_function
from flask_restful import reqparse, Api
from flask import jsonify, abort
from flask.ext.bcrypt import Bcrypt
from app import app
from models import user
from flask_jwt import JWT, current_identity
import sys

api = Api(app)
bcrypt = Bcrypt(app)


def abort_if_not_allowed(user_id):
    if (int(user_id) != int(current_identity.id)):
        abort(401)


parser = reqparse.RequestParser()
parser.add_argument('email')
parser.add_argument('password')
parser.add_argument('username')
parser.add_argument('domain')
parser.add_argument('newpassword')

from resources.user import User
from resources.user.User import UserHash
from resources.account import Account

api.add_resource(UserHash, '/users/<user_id>/hash', endpoint='hash')
api.add_resource(User, '/users/<user_id>', '/users')
api.add_resource(Account, '/users/<user_id>/accounts',
                 '/users/<user_id>/accounts/<acc_id>')


def authenticate(username, password):
    dbuser = user.User.query.filter_by(email=username).first()
    if dbuser and bcrypt.check_password_hash(dbuser.password,
                                             password):
        print('==== pw match ====', file=sys.stderr)
        return dbuser


def identity(payload):
    user_id = payload['identity']
    return user.User.query.filter_by(id=int(user_id)).first()


jwt = JWT(app, authenticate, identity)


@jwt.auth_response_handler
def custom_auth_response_callback(access_token, identity):
    print(identity.email, file=sys.stderr)
    retjson = {
        'token': 'JWT ' + access_token.decode('utf-8'),
        'user': {
            'id': identity.id,
            'email': identity.email,
            'maxAccounts': identity.slots,
        }
    }

    return jsonify(retjson)


# TODO: disable in production
if __name__ == '__main__':
    app.run(debug=True)
