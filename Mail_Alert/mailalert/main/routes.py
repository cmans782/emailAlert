from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask_login import login_required, current_user
from mailalert.main.forms import ComposeEmailForm, CreateMessageForm, StudentSearchForm
from mailalert.models import Message, Package, SentMail
from mailalert import db
from mailalert.main.utils import send_package_update_email

main = Blueprint('main', __name__)


@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    form = StudentSearchForm()
    if form.validate_on_submit():
        return redirect(url_for('packages.student_packages', student_id=form.student_id.data))
    return render_template('home.html', form=form)


@main.route("/composeEmail", methods=['GET', 'POST'])
@login_required
def compose_email():
    cc_recipients = ""
    composeEmailForm = ComposeEmailForm()
    createMessageForm = CreateMessageForm()
    if composeEmailForm.validate_on_submit():
        recipient_emails = composeEmailForm.recipient_email.data
        if composeEmailForm.cc_recipient.data:
            cc_recipients = composeEmailForm.cc_recipient.data
        message_id = request.form['options']
        message = Message.query.get(message_id)
        # log the email sent
        email = SentMail(employee=current_user, message=message)
        db.session.add(email)
        db.session.commit()
        send_package_update_email(
            message.content, recipient_emails, cc_recipients)
        flash("Email successfully sent!", "success")
        return redirect(url_for('main.home'))

    messages = Message.query.all()
    return render_template('composeEmail.html', title="Compose Email", composeEmailForm=composeEmailForm,
                           createMessageForm=createMessageForm, messages=messages)


@main.route("/_create_message", methods=['POST'])
@login_required
def create_message():
    form = CreateMessageForm()
    if form.validate_on_submit():
        message = Message(content=form.new_message.data)
        db.session.add(message)
        db.session.commit()
    else:
        flash("Message not long enough", "danger")
    return redirect(url_for('main.compose_email'))


@main.route("/_delete_message", methods=['POST'])
@login_required
def delete_message():
    message_id = request.form['deleteVal']
    if message_id:
        message = Message.query.get(message_id)
        db.session.delete(message)
        db.session.commit()
    else:
        flash("You must first select a message to delete!", "danger")
    return redirect(url_for('main.compose_email'))
