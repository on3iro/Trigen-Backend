from flask_restful import Resource
from flask_jwt import jwt_required
from app import db
from triserv import abort_if_not_allowed, parser
from models import user, account


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


api.add_resource(Account, '/users/<user_id>/accounts',
                 '/users/<user_id>/accounts/<acc_id>')
