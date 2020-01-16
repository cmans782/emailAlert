from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from mailalert.config import Config
from flask_wtf.csrf import CSRFProtect
from flask_admin import Admin
from celery import Celery
from mailalert.admin_views import EmployeeView, StudentView, HallView, \
    PackageView, SentMailView, LoginView, PhoneView, UtilsView, CeleryView


admin = Admin(name="Mail Alert", template_mode='bootstrap3')

db = SQLAlchemy()
bcrypt = Bcrypt()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'employees.login'
login_manager.login_message_category = 'info'
mail = Mail()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL,
                backend=Config.CELERY_BACKEND)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    admin.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    celery.conf.update(app.config)

    # Admin Panel
    from mailalert.models import Package, Employee, SentMail, Student, Hall, Login, Phone, Utils, Task
    admin.add_view(PackageView(Package, db.session))
    admin.add_view(EmployeeView(Employee, db.session))
    admin.add_view(StudentView(Student, db.session))
    admin.add_view(HallView(Hall, db.session))
    admin.add_view(SentMailView(SentMail, db.session))
    admin.add_view(LoginView(Login, db.session))
    admin.add_view(PhoneView(Phone, db.session))
    admin.add_view(UtilsView(Utils, db.session))
    admin.add_view(CeleryView(Task, db.session))

    from mailalert.employees.routes import employees  # import blueprint instance
    from mailalert.packages.routes import packages
    from mailalert.main.routes import main
    from mailalert.errors.handlers import errors
    app.register_blueprint(employees)  # register instances with our app
    app.register_blueprint(packages)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
