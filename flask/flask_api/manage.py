from app import create_app, db
from app.models import User, Role, Post, Category, Tag
from flask_migrate import Migrate, upgrade, MigrateCommand
from flask_script import Manager, Shell, Server


app = create_app('test')
manager = Manager(app)
migrate = Migrate(app, db)
server = Server(host='0.0.0.0', port=5000)


@app.context_processor
def make_shell_context():
    return dict(
        app=app, db=db, User=User, Role=Role
    )


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("runserver", server)
manager.add_command("db", MigrateCommand)


# HTTPIE (if self signed certificate): https --verify=no
if __name__ == '__main__':
    manager.run()
