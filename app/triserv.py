from __future__ import print_function
from flask_restful import reqparse, Resource, Api, abort
from flask import jsonify
from flask.ext.bcrypt import Bcrypt
from app import app
from app import db
from models import user, account
from flask_jwt import JWT, jwt_required, current_identity
import sys
import random
import sqlalchemy.exc

api = Api(app)
bcrypt = Bcrypt(app)


parser = reqparse.RequestParser()
parser.add_argument('email')
parser.add_argument('password')
parser.add_argument('username')
parser.add_argument('domain')
parser.add_argument('newpassword')


@jwt_required()
def abort_if_not_allowed(user_id):
    if (int(user_id) != int(current_identity.id)):
        abort(401, message='Keine Berechtigung')


class User(Resource):
    def generate_user_hash(self):
        uhash = random.getrandbits(128)
        return "%032x" % uhash

    @jwt_required()
    def get(self, user_id):
        abort_if_not_allowed(user_id)

        try:
            dbuser = user.User.query.filter_by(id=int(user_id)).first()
        except sqlalchemy.exc.SQLAlchemyError:
            abort(404, message='Nutzer konnte nicht gefunden werden.')

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

        try:
            db.session.add(new_user)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            abort(422, message='Diese E-Mail ist bereits registriert')

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
            abort(405, message='Action not supported')

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
            if (not dbuser):
                abort(404, message='Nutzerhash konnte nicht gefunden werden')
            retjson = {
                'hash': dbuser.userhash
            }
            return retjson

    class Slots(Resource):
        @jwt_required()
        def post(self, user_id, amount):
            abort_if_not_allowed(user_id)

            dbuser = user.User.query.filter_by(id=int(user_id)).first()
            dbuser.slots += int(amount)

            try:
                db.session.add(dbuser)
                db.session.commit()
            except:
                abort(418, 'Uuups, das hat nicht funktioniert')

            retjson = {
                'message': 'Slots wurden erweitert',
                'maxAccounts': dbuser.slots
            }
            return retjson

    api.add_resource(UserHash, '/users/<user_id>/hash', endpoint='hash')
    api.add_resource(Slots, '/users/<user_id>/slots/add/<amount>')


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

        return jsonify(retaccs)

    @jwt_required()
    def post(self, user_id):
        abort_if_not_allowed(user_id)
        args = parser.parse_args()

        dbuser = user.User.query.filter_by(id=int(user_id)).first()
        if (dbuser.slots <= len(dbuser.accounts)):
            abort(400, message='Maximale Slotanzahl erreicht')

        new_account = account.Account(args['username'], args['domain'])

        dbuser.accounts.append(new_account)

        try:
            db.session.add(dbuser)
            db.session.commit()
        except sqlalchemy.exc.IntegretyError:
            abort(422, message='Account existiert bereits')

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
        if (not dbacc):
            abort(404, message='Account nicht gefunden')

        dbacc.username = args['username']
        dbacc.domain = args['domain']

        try:
            db.session.add(dbacc)
            db.session.commit()
        except:
            abort(422, message='Eintrag konnte nicht bearbeitet werden')

        return {'domain': dbacc.domain, 'username': dbacc.username}

    @jwt_required()
    def delete(self, user_id, acc_id):
        abort_if_not_allowed(user_id)
        # TODO: test if acc_id belongs to user_id

        dbacc = account.Account.query.filter_by(id=int(acc_id)).first()
        if (not dbacc):
            abort(404, message='Account nicht gefunden')

        try:
            db.session.delete(dbacc)
            db.session.commit()
        except:
            abort(400, message='Account konnte nicht entfernt werden')

        return {'account_id': acc_id, 'message': 'deleted'}

api.add_resource(User, '/users/<user_id>', '/users')
api.add_resource(Account, '/users/<user_id>/accounts',
                 '/users/<user_id>/accounts/<acc_id>')


def authenticate(username, password):
    dbuser = user.User.query.filter_by(email=username).first()
    if dbuser and bcrypt.check_password_hash(dbuser.password,
                                             password):
        return dbuser
    abort(401, message='Passwort inkorrekt')


def identity(payload):
    user_id = payload['identity']
    dbuser = user.User.query.filter_by(id=int(user_id)).first()
    if (not dbuser):
        abort(404, message='Nutzer existiert nicht')
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
