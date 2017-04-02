# Account model
from app import db
from .base import Base


class Account(Base):
    __tablename__ = "accounts"

    # Username for the account
    username = db.Column(db.String(128), nullable=False)

    # Domain or name of the service
    domain = db.Column(db.String(256), nullable=False)

    # Instantiation
    def __init__(self, username, domain):
        self.username = username
        self.domain = domain

    def __repr__(self):
        return '<Account %r>' % (self.name)
