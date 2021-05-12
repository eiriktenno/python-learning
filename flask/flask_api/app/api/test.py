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


# User START ---------------------------------------------------------------

# _User - Register
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


# _User - Load User
# HTTPIE: http --json localhost:5000/api/ "email=<input>" "password=<input>"
@api.route('/load_user/', methods=['GET', 'POST'])
def load_user():
	username = request.json.get('username')
	user = User.query.filter_by(username=username).first()
	return jsonify(user.to_json())


# _User - List usernames
# HTTPIE: https --verify no --auth <email>:<password> --json localhost:5000/api/usernames/
@api.route('/usernames/', methods=['GET'])
@auth.login_required()
def list_usernames():
	username_list = [i.username for i in User.query.all()]
	return jsonify(username_list)


# _User - List users
# Return a list of users and user info. Add pagination?
@api.route('/users/', methods=['GET'])
@auth.login_required(role='admin')
def list_users():
	user_list = [
		user.to_json() for user in User.query.all()
	]
	return jsonify(user_list)


# _User - Edit
# http --auth <email>:<password> --json localhost:5000/api/users/edit/
@api.route('/users/edit/', methods=['POST'])
@auth.login_required()
def edit_user():
	user = g.user
	username = request.json.get('username')
	password = request.json.get('password')
	email = request.json.get('email')

	if password is not None:
		user.password = password

	if (request.json.get('username') is None) or (request.json.get('email') is None):
		abort(400)  # Missing argument

	username_check = User.query.filter_by(username=username).first()
	if (username_check is not None) and (username_check is not user):
		abort(400)  # User already exist

	email_check = User.query.filter_by(email=email).first()
	if (email_check is not None) and (email_check is not user):
		abort(400)  # Email already exist

	user.username = username
	user.email = email

	db.session.add(user)
	db.session.commit()
	return jsonify(user.to_json())


# _User - Admin Edit
@api.route('/users/admin/edit/<user_id>/', methods=['POST'])
@auth.login_required(role='admin')
def edit_user_admin(user_id):
	user = User.query.filter_by(id=user_id).first()

	if user is None:
		abort(400)

	username = request.json.get('username')
	password = request.json.get('password')
	email = request.json.get('email')

	if password is not None:
		user.password = password

	if (request.json.get('username') is None) or (request.json.get('email') is None):
		abort(400)  # Missing argument

	username_check = User.query.filter_by(username=username).first()
	if (username_check is not None) and (username_check is not user):
		abort(400)  # User already exist

	email_check = User.query.filter_by(email=email).first()
	if (email_check is not None) and (email_check is not user):
		abort(400)  # Email already exist

	user.username = username
	user.email = email

	db.session.add(user)
	db.session.commit()
	return jsonify(user.to_json())


# _User - Admin delete
@api.route('/users/admin/delete/<user_id>/', methods=['POST'])
@auth.login_required(role='admin')
def delete_user_admin(user_id):
	user = User.query.filter_by(id=user_id).first()
	print(user)
	username = user.username

	if user is None:
		abort(400)

	if user.role != "admin":
		db.session.delete(user)
		db.session.commit()
	else:
		abort(400)

	return {'result': 'User %s, been deleted' % username}

# User END ---------------------------------------------------------------


# TEST START ---------------------------------------------------------------

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

# TEST - END ---------------------------------------------------------------

# ROLES START ---------------------------------------------------------------

# _Roles - Get role


# _Roles - List of roles
@api.route('/roles/', methods=['GET'])
@auth.login_required(role='admin')
def list_roles():
	role_list = [
		role.to_json() for role in Role.query.all()
	]
	return jsonify(role_list)


# _Roles - Edit Role
@api.route('/roles/edit/<role_id>/', methods=['POST'])
@auth.login_required(role='admin')
def role_edit(role_id):
	role = Role.query.filter_by(id=role_id).first()

	if role is None:
		abort(400)

	name = request.json.get('name')

	if name is None:
		abort(400)

	name_check = Role.query.filter_by(name=name).first()
	if (name_check is not None) and (name_check is not name):
		abort(400)  # Name already used.

	role.name = name
	db.session.add(role)
	db.session.commit()

	return jsonify(role.to_json())


# _Roles - Delete Role
@api.route('/roles/delete/<role_id>/', methods=['POST'])
@auth.login_required(role='admin')
def role_delete(role_id):
	role = Role.query.filter_by(id=role_id).first()

	if role is None:
		abort(400)

	if role.name is 'admin':
		abort(400)

	name = role.name
	db.session.delete(role)
	db.session.commit()

	return {'result': 'Role %s, been deleted' % name}


# _Roles - Add Role
@api.route('/roles/add/', methods=['POST'])
@auth.login_required(role='admin')
def role_add():
	name = request.json.get('name')
	if name is None:
		abort(400)  # Missing argument
	if Role.query.filter_by(name=name).first() is not None:
		abort(400)  # User already exist
	role = Role(
		name=name
	)
	db.session.add(role)
	db.session.commit()
	return jsonify(role.to_json())

# ROLES END ---------------------------------------------------------------


# POST START ---------------------------------------------------------------

# _Post - Get post
@api.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
	post = Post.query.filter_by(id=post_id).first()
	if post is None:
		abort(400)
	return jsonify(post.to_json())

# _Post - List
@api.route('/posts/', methods=['GET'])
@auth.login_required(role='admin')
def list_posts():
	post_list = [
		post.to_json() for post in Post.query.all()
	]
	return jsonify(post_list)


# _Post - New
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


# _Post - Moderate
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


# _Post - Delete
@api.route('/posts/delete/<post_id>/', methods=['POST'])
def delete_post(post_id):
	post = Post.query.filter_by(id=post_id).first()

	if post is None:
		abort(400)

	title = post.title
	db.session.delete(post)
	db.session.commit()

	return {'result': 'Post %s, been deleted' % title}


# _Post - Admin Delete ???

# POST END ---------------------------------------------------------------

# Category START ---------------------------------------------------------------

# _Category - Get category
@api.route('/categories/<category_id>')
def get_category(category_id):
	category = Category.query.filter_by(id=category_id).first()

	if category is None:
		abort(400)

	return jsonify(category.to_json())


# _Category - List
@api.route('/categories/', methods=['GET'])
def list_categories():
	category_list = [
		category.to_json() for category in Category.query.all()
	]
	return jsonify(category_list)


# _Category - Edit
@api.route('/categories/edit/<category_id>', methods=['POST'])
def edit_category(category_id):
	priority = request.json.get('priority')
	display_name = request.json.get('display_name')
	custom_template = request.json.get('custom_template')
	custom_url = request.json.get('custom_url')
	# children = [] - LIST MORE WORK
	# parents = [] - LIST MORE WORK

	category = Category.query_filter_by(id=category_id).first()

	return 'Category: Edit Category'


# _Category - Delete
@api.route('/categories/delete/<category_id>', methods=['POST'])
def delete_category(category_id):
	return 'Category: Delete Category'


# _Category - Add
@api.route('/categories/add', methods=['POST'])
def add_category(category_id):
	return 'Category: Add Category.'

# Category END ---------------------------------------------------------------


# Tag START ---------------------------------------------------------------

# _Tag - List


# _Tag - Add


# _Tag - Delete


# _Tag - Edit


# Tag END ---------------------------------------------------------------

# Permissions START ---------------------------------------------------------------

# _Permissions - List


# _Permissions - Add


# _Permissions - Delete


# _Permissions -  Edit

# Permissions END ---------------------------------------------------------------
