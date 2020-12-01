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

    @property
    def password(self):
        raise AttributeError('Password is not readable.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def to_json(self):
        json_user = {
            'username': self.username
        }
        return json_user

    @staticmethod
    def from_json(json_user):
        username = json_user.get('username')
        if username is None:
            raise ValidationError('Empty username')
        return User(username=username)


class AnonymousUser(AnonymousUserMixin):
    pass


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


login_manager.anonymous_user = AnonymousUser
