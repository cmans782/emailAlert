from flask import url_for, redirect, render_template
from flask_mail import Message
from mailalert import mail
from mailalert.models import Employee
from flask_login import current_user
from functools import wraps
from mailalert.config import Config


def send_package_update_email(message, recipients, cc_recipients):
    msg = Message()
    msg.subject = 'Package Update'
    msg.sender = 'KutztownMail@gmail.com'
    msg.recipients = [recipients]
    msg.cc = [cc_recipients]
    msg.body = message

    mail.send(msg)


def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.allowed(access_level):
                return render_template('errors/403.html')
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
