from flask import jsonify, request, current_app, url_for,abort, g
from . import api
from ..models import User
from .. import db
from flask_httpauth import HTTPBasicAuth


auth = HTTPBasicAuth()


# HTTPIE: http --json localhost:5000/api/ "username=<input>" "email=<input>" "password=<input>"
@api.route('/register/', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    if (username is None) or (password is None) or (email is None):
        abort(400)  # Missing argument
    if User.query.filter_by(username=username).first() is not None:
        abort(400)  # User already exist
    if User.query.filter_by(email=email).first() is not None:
        abort(400)  # Email already exist
    user = User(
        username=username,
        email=email
    )
    user.password = password
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_json(user))


# HTTPIE: http --json localhost:5000/api/ "email=<input>" "password=<input>"
@api.route('/load_user/', methods=['POST'])
def load_user():
    email = request.json.get('username')
    user = User.query.filter_by(email=email).first()
    return jsonify(user.to_json(user))


# HTTPIE: http --auth <email>:<password> --json localhost:5000/api/test
@api.route('/test')
@auth.login_required()
def get_resources():
    return jsonify({'data': 'Hello, %s' % g.user.username})


@auth.verify_password
def verify_password(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True
