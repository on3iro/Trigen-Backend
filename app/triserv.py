from flask import jsonify
from flask_restful import reqparse, abort, Resource, Api
from app import app
from app import db
from models import user, account, users_accounts

api = Api(app)


parser = reqparse.RequestParser()
parser.add_argument('email')
parser.add_argument('password')
parser.add_argument('username')
parser.add_argument('domain')


class User(Resource):
    def get(self, user_id):
        dbuser = user.User.query.filter_by(id=int(user_id)).first()

        retuser = {
            'email': dbuser.email,
            'hash': dbuser.userhash,
            'slots': dbuser.slots
        }
        return retuser

    def post(self):
        args = parser.parse_args()
        new_user = user.User(args['email'], '1234')
        retuser = {
            'email': new_user.email,
            'password': new_user.password
        }
        db.session.add(new_user)
        db.session.commit()
        return retuser


class Account(Resource):
    def get(self, user_id):
        uarels = users_accounts.UsersAccounts.query.filter_by(
            userid=int(user_id))

        dbaccs = {}
        for uarel in uarels:
            dbacc = account.Account.query.filter_by(
                id=int(uarel.accountid)).first()
            dbaccs[uarel.accountid] = dbacc

        retaccs = {}
        for accid, acc in dbaccs.items():
            retacc = {
                'userid': user_id,
                'account_id': acc.id,
                'username': acc.username,
                'domain': acc.domain
            }
            retaccs[acc.id] = retacc

        return retaccs

    def post(self, user_id):
        args = parser.parse_args()
        new_account = account.Account(args['username'], args['domain'])

        db.session.add(new_account)
        db.session.commit()

        new_ua_rel = users_accounts.UsersAccounts(user_id, new_account.id)
        db.session.add(new_ua_rel)
        print(new_account.id)
        db.session.commit()

        retacc = {
            'userid': user_id,
            'account_id': new_account.id,
            'username': new_account.username,
            'domain': new_account.domain
        }
        return retacc

api.add_resource(User, '/users/<user_id>', '/users')
api.add_resource(Account, '/users/<user_id>/accounts')

# TODO: disable in production
if __name__ == '__main__':
    app.run(debug=True)
