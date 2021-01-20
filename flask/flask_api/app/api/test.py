from flask import jsonify, request, current_app, url_for, abort, g
from . import api
from ..models import User
from .. import db
from flask_httpauth import HTTPBasicAuth
from ..models import User, Role, Category, Post, Permission, Tag
from ..decorators import permission_required

'''
API methods:

Examples
	GET		|	Obtain information about a resource |	http://example.com/api/orders (retrieve order list)
	GET		|	Obtain information about a resource	|	http://example.com/api/orders/123 (retrieve order #123)
	POST 	| 	Create a new resource				|	http://example.com/api/orders (create a new order, from data provided with the request)
	PUT		|	Update a resource					|	http://example.com/api/orders/123 (update order #123, from data provided with the request)
	DELETE	|	Delete a resource					|	http://example.com/api/orders/123 (delete order #123)
'''

auth = HTTPBasicAuth()


# Role check for HTTPAuthe
@auth.get_user_roles
def get_user_roles(user):
	user = User.query.filter_by(email=user.username).first()
	return user.get_role()


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
	return jsonify(user.to_json())


# HTTPIE: http --json localhost:5000/api/ "email=<input>" "password=<input>"
@api.route('/load_user/', methods=['GET', 'POST'])
def load_user():
	username = request.json.get('username')
	user = User.query.filter_by(username=username).first()
	return jsonify(user.to_json())


# HTTPIE: http --auth <email>:<password> --json localhost:5000/api/test
@api.route('/test', methods=['GET'])
@auth.login_required()
def get_resources():
	return jsonify({'data': 'Hello, %s' % g.user.username})


@api.route('/testapi/', methods=['GET'])
def test_api():
	return {'result': "ERPA DERPA"}


@auth.verify_password
def verify_password(email, password):
	user = User.query.filter_by(email=email).first()
	if not user or not user.verify_password(password):
		return False
	g.user = user
	return True


# Return list of registered usernames
# HTTPIE: https --verify no --auth <email>:<password> --json localhost:5000/api/usernames/
@api.route('/usernames/', methods=['GET'])
@auth.login_required()
def list_usernames():
	username_list = [i.username for i in User.query.all()]
	return jsonify(username_list)


# Return a list of users and user info. Add pagination?
@api.route('/users/', methods=['GET'])
@auth.login_required(role='admin')
def list_users():
	user_list = [
		user.to_json() for user in User.query.all()
	]
	return jsonify(user_list)


# Return a list of roles
@api.route('/roles/', methods=['GET'])
@auth.login_required(role='admin')
def list_roles():
	role_list = [
		role.to_json() for role in Role.query.all()
	]
	return jsonify(role_list)


# Post - List
@api.route('/posts/', methods=['GET'])
@auth.login_required(role='admin')
def list_posts():
	pass


# Post - New
@api.route('/new_post/', methods=['POST'])
@auth.login_required(role='admin')
def new_post():
	pass


# Post - Moderate
@api.route('/edit_post/', methods=['POST'])
@auth.login_required(role='admin')
def edit_post():
	pass


# Category - Navbar item
@api.route('/categories/', methods=['GET'])
def list_categories():
	category_list = [
		category.to_json() for category in Category.query.all()
	]
	return jsonify(category_list)
