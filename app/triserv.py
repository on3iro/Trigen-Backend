from __future__ import print_function
from flask_restful import reqparse, Resource, Api
from flask import jsonify, abort
from app import app
from app import db
from models import user, account
from werkzeug.security import safe_str_cmp
from flask_jwt import JWT, jwt_required, current_identity
import sys
import random

api = Api(app)


parser = reqparse.RequestParser()
parser.add_argument('email')
parser.add_argument('password')
parser.add_argument('username')
parser.add_argument('domain')
parser.add_argument('newpassword')


@jwt_required()
def abort_if_not_allowed(user_id):
    if (int(user_id) != int(current_identity.id)):
        abort(401)


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
        new_user = user.User(args['email'], args['password'])
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

    api.add_resource(UserHash, '/users/<user_id>/hash', endpoint='hash')


class Account(Resource):
    @jwt_required()
    def get(self, user_id):
        abort_if_not_allowed(user_id)

        # TODO: getting all accounts for a user should be in usermodel
        dbuser = user.User.query.filter_by(id=int(user_id)).first()
        dbaccs = dbuser.accounts

        retaccs = []
        for acc in dbaccs:
            retacc = {
                'id': acc.id,
                'username': acc.username,
                'domain': acc.domain
            }
            retaccs.append(retacc)

        return retaccs

    @jwt_required()
    def post(self, user_id):
        abort_if_not_allowed(user_id)
        args = parser.parse_args()

        dbuser = user.User.query.filter_by(id=int(user_id)).first()
        if (dbuser.slots <= len(dbuser.accounts)):
            return {'message': 'No more slots available'}

        new_account = account.Account(args['username'], args['domain'])

        dbuser.accounts.append(new_account)

        db.session.add(dbuser)
        db.session.commit()

        retacc = {
            'userid': user_id,
            'account_id': new_account.id,
            'username': new_account.username,
            'domain': new_account.domain
        }
        return retacc

    @jwt_required()
    def put(self, user_id, acc_id):
        abort_if_not_allowed(user_id)
        args = parser.parse_args()
        # TODO: test if acc_id belongs to user_id

        dbacc = account.Account.query.filter_by(id=int(acc_id)).first()
        dbacc.username = args['username']
        dbacc.domain = args['domain']

        db.session.add(dbacc)
        db.session.commit()

        return {'domain': dbacc.domain, 'username': dbacc.username}

    @jwt_required()
    def delete(self, user_id, acc_id):
        abort_if_not_allowed(user_id)
        # TODO: test if acc_id belongs to user_id

        dbacc = account.Account.query.filter_by(id=int(acc_id)).first()
        db.session.delete(dbacc)
        db.session.commit()

        return {'account_id': acc_id, 'message': 'deleted'}

api.add_resource(User, '/users/<user_id>', '/users')
api.add_resource(Account, '/users/<user_id>/accounts',
                 '/users/<user_id>/accounts/<acc_id>')


def authenticate(username, password):
    dbuser = user.User.query.filter_by(email=username).first()
    if dbuser and safe_str_cmp(dbuser.password,
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
    app.run(debug=True, host='0.0.0.0', port=5000)
