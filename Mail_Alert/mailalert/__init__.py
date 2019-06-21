from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from mailalert.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'employees.login'
login_manager.login_message_category = 'info'

mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from mailalert.employees.routes import employees  #import blueprint instance
    from mailalert.packages.routes import packages  
    from mailalert.main.routes import main  
    app.register_blueprint(employees)  # register instances with our app
    app.register_blueprint(packages)
    app.register_blueprint(main)

    return app