from flask import Blueprint

main = Blueprint(
    name='main',
    import_name=__name__
)

from . import views