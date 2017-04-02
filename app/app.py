# Initialize the app
# Import all the stuff
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# Define the WSGI application object
app = Flask(__name__)


# Load configurations
app.config.from_object('config')


# Define the database object which is imported
# by modules
db = SQLAlchemy(app)
from models import base, user, account, users_accounts

# Build the database
db.create_all()
