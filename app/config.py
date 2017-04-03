# Configuration
import os

# enabling development environment
DEBUG = True

# Application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
print(BASE_DIR)

# Setting up the database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'trigen.db')
print(SQLALCHEMY_DATABASE_URI)
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "ohchao3E"

# Secret key for signing cookies
SECRET_KEY = "sha3Xi4A"

# JWT settings
JWT_AUTH_URL_RULE = "/login"
JWT_AUTH_USERNAME_KEY = "email"
