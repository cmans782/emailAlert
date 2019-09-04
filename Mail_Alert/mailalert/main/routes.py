import os
import csv
from werkzeug.utils import secure_filename
from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask_login import login_required, current_user
from mailalert.main.forms import ComposeEmailForm, CreateMessageForm, StudentSearchForm
from mailalert.models import Message, Package, SentMail, Student, Hall
from mailalert import db
from mailalert.config import Config
from mailalert.main.utils import send_package_update_email, allowed_file

main = Blueprint('main', __name__)


@main.route("/setup", methods=['POST'])
@login_required
def setup():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No selected file')
        return redirect('main.home')
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect('main.home')
    if file and allowed_file(file.filename):
        data = file.read().decode('utf-8')
        data = data.split('\r\n')

        # for student in data:
        # data = [None if value is '' else value for value in student]

        # drop Student model
        db.session.query(Student).delete()
        db.session.commit()

        for student in data:
            student = student.split(',')
            student_hall = Hall.query.filter_by(name=student[6]).first()
            student_id_exists = Student.query.filter_by(
                student_id=student[0]).first()
            student_email_exists = Student.query.filter_by(
                email=student[3]).first()
            if student[5] == '':
                student[5] = None
            else:
                student_phone_exists = Student.query.filter_by(
                    phone_number=student[5]).first()
            if student_id_exists:
                flash('Error: Student ID\'s cannot be duplicated', 'danger')
                return redirect(url_for('main.home'))
            if student_email_exists:
                flash('Error: Student email addresses cannot be duplicated', 'danger')
                return redirect(url_for('main.home'))
            if student_phone_exists:
                flash('Error: Student phone numbers cannot be duplicated', 'danger')
                return redirect(url_for('main.home'))
            else:
                new_student = Student(student_id=student[0], first_name=student[1], last_name=student[2],
                                      email=student[3], room_number=student[4], phone_number=student[5], hall=student_hall)
                db.session.add(new_student)
        flash('Students successfully added!', 'success')
        db.session.commit()

    return redirect(url_for('main.home'))


@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    setup = request.args.get('setup')
    packages = Package.query.filter_by(perishable=True, status="Active").all()
    form = StudentSearchForm()
    if form.validate_on_submit():
        return redirect(url_for('packages.student_packages', student_id=form.student_id.data))
    return render_template('home.html', form=form, setup=setup, packages=packages)


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
