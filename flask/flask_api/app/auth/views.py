from . import auth
from .forms import LoginForm, RegisterForm
from ..models import User
from .. import db
from flask import redirect, url_for, render_template
from flask_login import login_user, logout_user, current_user


@auth.route('/')
def index():
	return 'Auth Index'


@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		user = User(
			username=form.username.data,
			email=form.email.data,
			password=form.password.data
		)
		db.session.add(user)
		db.session.commit()
		return redirect(url_for('main.index'))
	return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me)
			return redirect(url_for('main.index'))
	return render_template('auth/login.html', form=form)


@auth.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('main.index'))
