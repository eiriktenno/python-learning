from . import db, login_manager
from app.exceptions import ValidationError
from flask_login import UserMixin, AnonymousUserMixin, current_user
from werkzeug.security import check_password_hash, generate_password_hash


class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, index=True, primary_key=True)
	username = db.Column(db.String(128), index=True, unique=True)
	email = db.Column(db.String(128), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), index=True)

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
			'email': self.email
		}
		return json_user

	@staticmethod
	def from_json(json_user):
		username = json_user.get('username')
		if username is None:
			raise ValidationError('Empty username')
		return User(username=username)

	def get_role(self):
		print("Role checking")
		if self.role is not None:
			return self.role.name
		else:
			return ''


	# def serialize(self):
	#     return {
	#         'username': self.username,
	#         'email': self.email
	#     }


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
