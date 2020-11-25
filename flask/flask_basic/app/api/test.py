from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User
from .. import db


@api.route('/', methods=['POST'])
def new_user():
    user = User.from_json(request.json)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_json(user))
