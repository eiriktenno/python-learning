from . import api
from .. import db
from ..models import User, Role, Category, Post, Permission, Tag
from flask import jsonify, request, current_app, url_for, abort, g
from flask_httpauth import HTTPBasicAuth
from slugify import slugify
from datetime import datetime


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


# Role check for HTTPAuth
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
	post_list = [
		post.to_json() for post in Post.query.all()
	]
	return post_list


# Post - New
# HTTPIE: https --verify no --auth <email>:<password> --json localhost:5000/api/new_post/ "title=test123"
# "body=bodytest 123231"
@api.route('/new_post/', methods=['POST'])
@auth.login_required(role='admin')
def new_post():
	title = request.json.get('title')
	body = request.json.get('body')
	slug = slugify(title)
	author = User.query.filter_by(email=auth.current_user()).first()
	if (title is None) or (body is None):
		abort(400)  # Missing argument
	if Post.query.filter_by(title=title).first() is not None:
		abort(400)  # Title already exist
	if Post.query.filter_by(slug=slug).first() is not None:
		abort(400)  # Slug already exist
	post = Post(
		title=title,
		body=body,
		author=author,
		slug=slug
	)
	db.session.add(post)
	db.session.commit()
	return jsonify(post.to_json())


# Post - Moderate
@api.route('/edit_post/<slug>', methods=['POST'])
@auth.login_required(role='admin')
def edit_post(slug):
	post = Post.query.filter_by(slug=slug).first()
	if post is None:
		abort(400)		# Slug doesn't exist

	title = request.json.get('title')
	body = request.json.get('body')
	slug = slugify(title)
	date_modified = datetime.utcnow
	moderator = User.query.filter_by(email=auth.current_user()).first()
	image = ''

	if (title is None) or (body is None):
		abort(400)  # Missing argument
	if Post.query.filter_by(title=title).first() is not None:
		abort(400)  # Title already exist
	if Post.query.filter_by(slug=slug).first() is not None:
		abort(400)  # Slug already exist

	post.title = title
	post.body = body
	post.moderator = moderator
	post.slug = slug
	post.date_modified = date_modified
	post.image = image

	db.session.add(post)
	db.session.commit()
	return jsonify(post.to_json())


# Category - Navbar item
@api.route('/categories/', methods=['GET'])
def list_categories():
	category_list = [
		category.to_json() for category in Category.query.all()
	]
	return jsonify(category_list)
