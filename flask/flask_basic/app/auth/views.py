from . import auth


@auth.route('/')
def auth_index():
    return 'Auth Index'
