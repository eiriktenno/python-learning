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

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.role is None:
			default_role = Role.query.filter_by(default=True).first()
			if default_role is not None:
				self.role = default_role


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
		import forgery_py
		from sqlalchemy.exc import IntegrityError

		for i in range(quantity):
			u = User(
				username=forgery_py.internet.user_name(),
				email=forgery_py.internet.email_address(),
				password_hash=forgery_py.lorem_ipsum.word()
			)
			db.session.add(u)

			try:
				db.session.commit()
			except IntegrityError:
				db.session.rollback()


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
	default = db.Column(db.Boolean)
	users = db.relationship('User', backref='role', lazy='dynamic')

	def to_json(self):
		json_role = {
			'name': self.name,
			'categories': ''
		}
		return json_role

	@staticmethod
	def insert_roles():
		admin = Role(name='admin', default=False)
		moderator = Role(name='moderator', default=False)
		user = Role(name='user', default=True)
		db.session.add_all([admin, moderator, user])
		db.session.commit()


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
	date_modified = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	image = db.Column(db.String())
	moderator = db.Column(db.String(128))

	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

	def to_json(self):
		json_post = {
			'title': self.title if self.title is not None else '',
			'slug': self.slug if self.slug is not None else '',
			'body': self.body if self.body is not None else '',
			'timestamp': self.timestamp if self.timestamp is not None else '',
			'image': self.image if self.image is not None else '',
			'author': self.author.username,
			'date_modified': self.date_modified if self.date_modified is not None else '',
			'moderator': self.moderator if self.moderator is not None else ''
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
	Role.insert_roles()
	admin_role = Role.query.filter_by(name='admin').first()
	admin_user = User(
		username='admin',
		password='123456',
		email='admin@admin.admin',
		role=admin_role
	)
	db.session.add_all([admin_role, admin_user])
	db.session.commit()

	User.generate_fake_data(100)
