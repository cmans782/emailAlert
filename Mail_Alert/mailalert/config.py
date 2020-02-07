from datetime import timedelta
import json


with open('/etc/MailAlert_config.json') as config_file:
    # json.load turns the config file into a python dictionary
    config = json.load(config_file)


class Config:
    SECRET_KEY = config.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    # remove sqlalchemy warning
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # set timeout session
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=120)

    # theme for admin panel. can find other themes at http://bootswatch.com/3/
    FLASK_ADMIN_SWATCH = 'lumen'

    ALLOWED_EXTENSIONS = {'csv'}

    # SQLALCHEMY_ECHO = True

    TIMEZONE = 'US/Eastern'
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    # Celery
    CELERY_BROKER_URL = config.get('CELERY_BROKER_URL')
    CELERY_BACKEND = config.get('CELERY_BACKEND')

    # Original Version
    # MAIL_SERVER = 'email-smtp.us-east-1.amazonaws.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = config.get('MAIL_USERNAME')
    # MAIL_PASSWORD = config.get('MAIL_PASSWORD')
    
    # Link to PackageAlerts@getmailalert.com
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = config.get('MAIL_USERNAME')
    MAIL_PASSWORD = config.get('MAIL_PASSWORD')
    
    # suppress emails from being sent
    TESTING = True
