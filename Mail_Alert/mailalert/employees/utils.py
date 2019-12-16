from flask import url_for
from flask_mail import Message
from mailalert import mail, bcrypt, db
from sqlalchemy import event
from mailalert.models import Employee
from password_generator import PasswordGenerator


def send_reset_email(employee):
    """
    Send email to employee with a link to reset their email

    Parameters:
        employee - an employee object

    Return: 
        None
    """
    token = employee.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='KutztownMail@gmail.com', recipients=[employee.email])
    msg.body = f"""To reset your password, visit the following link:
{url_for('employees.reset_token', token=token, _external=True)}

If you did not make this request then please ignore this email.
"""

    mail.send(msg)

    return


def generate_random_string():
    """
    Generate random string to be used as password

    Return: 
        Random password
    """
    password = PasswordGenerator()
    password.minlen = 8
    password.maxlen = 10
    password.excludeschars = "!$\"\'^()."

    return password.generate()


def send_reset_password_email(employee, password):
    """
    Send email to newly added employee with their temp password
    and supply a link to reset their password

    Parameters:
        employee - employee object 
        password - temp password for the new user

    Return: 
        None
    """
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

    return


@event.listens_for(Employee.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    """
    hash user password whenever Employee.password value is changed

    Return: 
        Hashed password
    """
    if value != oldvalue:
        return bcrypt.generate_password_hash(value).decode(
            'utf-8')
    return value
