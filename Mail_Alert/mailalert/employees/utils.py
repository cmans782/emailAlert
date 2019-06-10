from flask import url_for
from flask_mail import Message
from mailalert import mail


def send_reset_email(employee):
    token = employee.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[employee.email])
    msg.body = f"""To reset your password, visit the following link:
{url_for('employees.reset_token', token=token, _external=True)}

If you did not make this request then please ignore this email.
"""

    mail.send(msg)