# User model
from app import db
from .base import Base
import string
import random


class User(Base):
    __tablename__ = "users"

    # Email (used as the username on our site)
    email = db.Column(db.String(128), nullable=False, unique=True)

    # Hashed password
    password = db.Column(db.String(192), nullable=False)
    # User specific hash for password generation

    userhash = db.Column(db.String(192), nullable=False)

    # Total number of available slots
    slots = db.Column(db.SmallInteger, nullable=False)

    # Instanciation
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.userhash = ''.join(random.choices
                                (string.ascii_uppercase + string.digits, k=8))
        self.slots = 5

    def __repr__(self):
        return '<User %r>' % (self.name)
