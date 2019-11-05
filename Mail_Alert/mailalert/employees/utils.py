from flask import url_for, flash
from flask_mail import Message
from mailalert import mail, bcrypt, db
from sqlalchemy import event
from mailalert.models import Employee, Student, Hall, Phone
import string
from random import choice, randint
import numpy as np
from datetime import datetime


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
    min_char = 8
    max_char = 12
    allchar = string.ascii_letters + string.punctuation + string.digits
    password = "".join(choice(allchar)
                       for x in range(randint(min_char, max_char)))
    return password


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
