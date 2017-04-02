# Mapping users to accounts
from app import db


class UsersAccounts(db.Model):
    __tablename__ = "users_accounts"

    # User ID
    userid = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    # Account ID
    accountid = db.Column(db.Integer, db.ForeignKey('accounts.id'),
                          primary_key=True)

    def __init__(self, userid, accid):
        self.userid = userid
        self.accountid = accid
