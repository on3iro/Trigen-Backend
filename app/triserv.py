from flask import Flask
from flask_restful import reqparse, abort, Resource, Api

app = Flask(__name__)
api = Api(app)

USERS = {
    '1': {'unique hash': '3h4ncj9', 'email': 'user1@simplel.de'},
    '2': {'unique hash': 's8doh3l', 'email': 'user2@simplel.de'},
    '3': {'unique hash': 'M8mHq1l', 'email': 'user3@simplel.de'},
}

parser = reqparse.RequestParser()
parser.add_argument('users')


def abort_if_user_doesnt_exist(user_id):
    if user_id not in USERS:
        abort(404, message="User {} does not exist".format(user_id))


class User(Resource):
    def get(self, user_id):
        abort_if_user_doesnt_exist(user_id)
        return USERS[user_id]

api.add_resource(User, '/users/<user_id>')

# TODO: disable in production
if __name__ == '__main__':
    app.run(debug=True)
