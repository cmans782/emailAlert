import os
import csv
from werkzeug.utils import secure_filename
from flask import render_template, Blueprint, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from mailalert.main.forms import ComposeEmailForm, CreateMessageForm, StudentSearchForm
from mailalert.models import Message, Package, SentMail, Student, Hall
from mailalert import db
from mailalert.config import Config
from mailalert.main.utils import send_package_update_email

main = Blueprint('main', __name__)


@main.route("/get_halls", methods=['POST'])
@login_required
def get_halls():
    hall_list = Hall.query.all()
    hall_list = [hall.name for hall in hall_list]
    # remove the current users hall because it is already being displayed
    hall_list.remove(current_user.hall.name)
    return jsonify({'halls': hall_list})


@main.route("/change_working_hall", methods=['POST'])
@login_required
def change_working_hall():
    new_hall = request.form.get('new_hall', None)
    hall = Hall.query.filter_by(name=new_hall).first()
    if not hall:
        return jsonify({'error', 'could not find that hall'})
    current_user.hall = hall
    db.session.commit()
    return jsonify({'success': 'success'})


# @main.route("/composeEmail", methods=['GET', 'POST'])
# @login_required
# def compose_email():
#     cc_recipients = ""
#     composeEmailForm = ComposeEmailForm()
#     createMessageForm = CreateMessageForm()
#     if composeEmailForm.validate_on_submit():
#         recipient_email = composeEmailForm.recipient_email.data
#         if composeEmailForm.cc_recipient.data:
#             cc_recipients = composeEmailForm.cc_recipient.data
#         message_id = request.form['options']
#         message = Message.query.get(message_id)
#         student = Student.query.filter_by(email=recipient_email).first()
#         if not student:
#             flash('Error getting student', 'danger')
#             return redirect(url_for('main.compose_email'))
#         # log the email sent
#         sent_mail = SentMail(employee=current_user,
#                              student=student, message=message)
#         db.session.add(sent_mail)
#         db.session.commit()
#         send_package_update_email(
#             message.content, recipient_email, cc_recipients)
#         flash("Email successfully sent!", "success")
#         return redirect(url_for('packages.home'))

#     messages = Message.query.all()
#     return render_template('composeEmail.html', title="Compose Email", composeEmailForm=composeEmailForm,
#                            createMessageForm=createMessageForm, messages=messages)


# @main.route("/_create_message", methods=['POST'])
# @login_required
# def create_message():
#     form = CreateMessageForm()
#     if form.validate_on_submit():
#         message = Message(content=form.new_message.data)
#         db.session.add(message)
#         db.session.commit()
#     else:
#         flash("Message not long enough", "danger")
#     return redirect(url_for('main.compose_email'))


# @main.route("/_delete_message", methods=['POST'])
# @login_required
# def delete_message():
#     message_id = request.form['deleteVal']
#     if message_id:
#         message = Message.query.get(message_id)
#         db.session.delete(message)
#         db.session.commit()
#     else:
#         flash("You must first select a message to delete!", "danger")
#     return redirect(url_for('main.compose_email'))
