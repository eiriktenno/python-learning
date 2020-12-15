from functools import wraps
from flask import abort, g
from .models import Role


def permission_required(role, auth):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			print(role)
			try:
				print(auth.current_user())
			except:
				print('Current User no working')
			return f(*args, **kwargs)
		return decorated_function
	return decorator
