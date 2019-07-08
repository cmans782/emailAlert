from flask import url_for
from flask_mail import Message
from mailalert import mail

def send_package_update_email(message, recipients, cc_recipients):
    msg = Message()
    msg.subject = 'Package Update'
    msg.sender = 'noreply@demo.com'
    msg.recipients = [recipients]
    msg.cc = [cc_recipients]
    msg.body = message

    mail.send(msg)