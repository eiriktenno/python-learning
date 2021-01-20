from . import db, login_manager
from app.exceptions import ValidationError
from datetime import datetime
from flask_login import UserMixin, AnonymousUserMixin, current_user
from werkzeug.security import check_password_hash, generate_password_hash


# Category parent/child relation
category_tree_table = db.Table(
	'category_tree',
	db.Column('parent_id', db.Integer, db.ForeignKey('categories.id')),
	db.Column('children_id', db.Integer, db.ForeignKey('categories.id'))
)


class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, index=True, primary_key=True)
	username = db.Column(db.String(128), index=True, unique=True)
	email = db.Column(db.String(128), index=True, unique=True)
	password_hash = db.Column(db.String(128))

	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), index=True)
	posts = db.relationship('Post', backref='author', lazy='dynamic')

	@property
	def password(self):
		raise AttributeError('Password is not readable.')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def to_json(self):
		json_user = {
			'username': self.username,
			'email': self.email,
			'role': self.role.to_json() if self.role is not None else '',
			'posts': [post.to_json() for post in self.posts],
			'categories': ''
		}
		return json_user

	@staticmethod
	def from_json(json_user):
		username = json_user.get('username')
		if username is None:
			raise ValidationError('Empty username')
		return User(username=username)

	def get_role(self):
		if self.role is not None:
			return self.role.name
		else:
			return None

	@staticmethod
	def generate_fake_data(quantity):
		pass


class AnonymousUser(AnonymousUserMixin):
	pass


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


login_manager.anonymous_user = AnonymousUser


class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, index=True, primary_key=True)
	name = db.Column(db.String(128), index=True, unique=True)
	users = db.relationship('User', backref='role', lazy='dynamic')

	def to_json(self):
		json_role = {
			'name': self.name,
			'categories': ''
		}
		return json_role

	@staticmethod
	def insert_roles():
		admin = Role(name='admin')

		moderator = Role(name='moderator')
		user = Role(name='user')
		db.session.add_all([admin, moderator, user])


class Permission(db.Model):
	__tablename__ = 'permissions'
	id = db.Column(db.Integer, index=True, primary_key=True)
	name = db.Column(db.String(128), index=True, unique=True)

	def to_json(self):
		pass

	@staticmethod
	def generate_fake_data(quantity):
		pass


class Post(db.Model):
	__tablename__ = 'posts'
	id = db.Column(db.Integer, index=True, primary_key=True)
	title = db.Column(db.String(128), index=True, unique=True)
	slug = db.Column(db.String(128), index=True, unique=True)
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	image = db.Column(db.String())

	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

	def to_json(self):
		json_post = {
			'title': self.title,
			'slug': self.slug,
			'body': self.body,
			'timestamp': self.timestamp,
			'image': self.image,
			'author': self.author.username
		}
		return json_post

	@staticmethod
	def generate_fake_data(quantity):
		pass


# http --json localhost:5000/api/categories/
class Category(db.Model):
	__tablename__ = 'categories'
	id = db.Column(db.Integer, index=True, primary_key=True)

	# Priority: To adjust order for navbar
	priority = db.Column(db.Integer, default=100)

	# Display name: Display name in navbar
	display_name = db.Column(db.String(128))

	# Custom Template: Settings for custom template or not.
	custom_template = db.Column(db.Boolean, default=False)
	custom_template_url = db.Column(db.String(128), default='')

	# list for children to category
	childes = db.relationship(
		'Category',
		secondary=category_tree_table,
		primaryjoin=(category_tree_table.c.parent_id == id),
		secondaryjoin=(category_tree_table.c.children_id == id),
		backref=db.backref('parents', lazy='dynamic'),
		lazy='dynamic'
	)

	def to_json(self):
		json_category = {
			'priority': self.priority,
			'display_name': self.display_name,
			'custom_template': self.custom_template,
			'custom_template_url': self.custom_template_url,
			'childes': [child.display_name for child in self.childes],
			'parents': [parent.display_name for parent in self.parents]
		}
		return json_category

	@staticmethod
	def generate_fake_data(quantity):
		pass


class Tag(db.Model):
	__tablename__ = 'tags'
	id = db.Column(db.Integer, index=True, primary_key=True)
	name = db.Column(db.String(128), index=True, unique=True)

	def to_json(self):
		pass

	@staticmethod
	def generate_fake_data(quantity):
		pass


def generate_fake_data():
	pass
