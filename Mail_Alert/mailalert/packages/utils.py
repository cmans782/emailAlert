
from flask_mail import Message
from mailalert import mail
from flask import url_for, render_template


def send_new_package_email(student, num_packages):
    msg = Message('Kutztown Package Update',
                  sender='KutztownMail@gmail.com',
                  recipients=[student.email])

    msg.html = render_template(
        'new_package_email.html', num_packages=num_packages, student=student)
    mail.send(msg)


def string_to_bool(s):
    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        return ValueError
