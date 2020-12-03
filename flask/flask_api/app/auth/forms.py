from app.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, \
	Length, Regexp
import email_validator


class LoginForm(FlaskForm):
	email = StringField('Email: ', validators=[DataRequired()])
	password = PasswordField('Password: ', validators=[DataRequired()])
	remember_me = BooleanField('Remember me')
	submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
	username = StringField('Username: ', validators=[DataRequired(), Regexp(
		'^[A-Za-z][A-Za-z0-9_.]*$', 0,
		'Username must have only letters, '
		'numbers, dots or underscores'), Length(1, 64)])
	email = StringField('Email: ', validators=[DataRequired(), Email(), Length(1, 64)])
	password = PasswordField('Password: ', validators=[
		DataRequired(),
		EqualTo('password2', message='Passwords must match.')
	])
	password2 = PasswordField('Confirm password: ', validators=[DataRequired()])
	submit = SubmitField('Register')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already taken.')

	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('Username already taken.')
