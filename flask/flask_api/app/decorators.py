from functools import wraps
from flask import abort, g
from .models import Role


def permission_required(role, current_user):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			print(role)
			print(current_user.username)
			return f(*args, **kwargs)
		return decorated_function
	return decorator
