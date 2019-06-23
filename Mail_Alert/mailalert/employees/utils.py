from flask import url_for
from flask_mail import Message
from mailalert import mail
import string
from random import choice, randint


def send_reset_email(employee):
    token = employee.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[employee.email])
    msg.body = f"""To reset your password, visit the following link:
{url_for('employees.reset_token', token=token, _external=True)}

If you did not make this request then please ignore this email.
"""

    mail.send(msg)


def generate_random_string():
    min_char = 8
    max_char = 12
    allchar = string.ascii_letters + string.punctuation + string.digits
    password = "".join(choice(allchar) for x in range(randint(min_char, max_char)))
    print ("This is your password : ",password)
    return password


def send_temp_password_email(employee, password):
    msg = Message('Temporary Password', sender='noreply@demo.com', recipients=[employee.email])
    msg.body = f"""You have just been added to the Kutztown Mail Alert team! 

Your temporary password is:
{password}
To reset your password, visit the following link:
{url_for('employees.reset_password', _external=True)}

if you did not make this request then please ignore this email.
"""
    mail.send(msg)