
from flask_mail import Message
from mailalert import mail


def send_new_package_email(student_email, num_packages):
    msg = Message('Kutztown Package Update',
                  sender='noreply@demo.com', recipients=[student_email])
    if num_packages > 1:
        msg.body = f"You have {num_packages} packages ready to be picked up!"
    else:
        msg.body = f"You have {num_packages} package ready to be picked up!"

    mail.send(msg)


def string_to_bool(s):
    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        return ValueError
