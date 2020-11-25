from . import db
from app.exceptions import ValidationError


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, index=True, primary_key=True)
    username = db.Column(db.String(128), index=True, unique=True)

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
