from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User
from .. import db


# HTTPIE: http --json localhost:5000/api/ "username=<input>"
@api.route('/', methods=['POST'])
def new_user():
    user = User.from_json(request.json)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_json(user))


@api.route('/load_user/', methods=['POST'])
def load_user():
    username = request.json.get('username')
    user = User.query.filter_by(username=username).first()
    return jsonify(user.to_json(user))
