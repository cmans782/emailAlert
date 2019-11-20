from flask import url_for, flash
from flask_mail import Message
from mailalert import mail, bcrypt, db
from sqlalchemy import event
from mailalert.models import Employee, Student, Hall, Phone
import string
from random import choice, randint
import numpy as np
from datetime import datetime
from password_generator import PasswordGenerator


def send_reset_email(employee):
    token = employee.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='KutztownMail@gmail.com', recipients=[employee.email])
    msg.body = f"""To reset your password, visit the following link:
{url_for('employees.reset_token', token=token, _external=True)}

If you did not make this request then please ignore this email.
"""

    mail.send(msg)


def generate_random_string():
    password = PasswordGenerator()
    password.minlen = 8
    password.maxlen = 10
    password.excludeschars = "!$\"\'^()."

    return password.generate()


def send_reset_password_email(employee, password):
    msg = Message('Temporary Password', sender='KutztownMail@gmail.com',
                  recipients=[employee.email])
    msg.body = f"""You have just been added to the Kutztown Mail Alert team! 
Your temporary password is:

{password}

In order to login, you must first reset your password.
To reset your password, visit the following link:
{url_for('employees.reset_password', _external=True)}

if you did not make this request then please ignore this email.
"""
    mail.send(msg)


@event.listens_for(Employee.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    if value != oldvalue:
        return bcrypt.generate_password_hash(value).decode(
            'utf-8')
    return value
