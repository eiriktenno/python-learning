from . import auth
from .forms import LoginForm, RegisterForm
from ..models import User
from .. import db
from flask import redirect, url_for, render_template


@auth.route('/')
def auth_index():
    return 'Auth Index'


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        print("123456")
        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET'])
def login():
    return 'LOGIN'


@auth.route('/logout')
def logout():
    return 'Logout'
