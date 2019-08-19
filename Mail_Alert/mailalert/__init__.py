from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from mailalert.config import Config
from flask_wtf.csrf import CSRFProtect
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


db = SQLAlchemy()

admin = Admin(name="Mail Alert", template_mode='bootstrap3')

bcrypt = Bcrypt()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'employees.login'
login_manager.login_message_category = 'info'

mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    admin.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # Admin Panel
    from mailalert.models import Package, Employee, Message, SentMail, Student, Hall, Login
    admin.add_view(ModelView(Package, db.session))
    admin.add_view(ModelView(Employee, db.session))
    admin.add_view(ModelView(Message, db.session))
    admin.add_view(ModelView(Student, db.session))
    admin.add_view(ModelView(Hall, db.session))
    admin.add_view(ModelView(SentMail, db.session))
    admin.add_view(ModelView(Login, db.session))

    from mailalert.employees.routes import employees  # import blueprint instance
    from mailalert.packages.routes import packages
    from mailalert.main.routes import main
    from mailalert.errors.handlers import errors
    app.register_blueprint(employees)  # register instances with our app
    app.register_blueprint(packages)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
