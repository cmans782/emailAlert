import os
import csv
from werkzeug.utils import secure_filename
from flask import render_template, Blueprint, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from mailalert.main.forms import ComposeEmailForm, CreateMessageForm, StudentSearchForm
from mailalert.models import Message, Package, SentMail, Student, Hall
from mailalert import db
from mailalert.config import Config
from mailalert.main.utils import send_package_update_email, clean_student_data, \
    validate_student_data, update_student_data, error_columns, allowed_file
import pandas as pd

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


@main.route("/upload_csv", methods=['POST'])
@login_required
def upload_csv():
    columns = ['USERNAME', 'FIRST NAME', 'LAST NAME',
               'BUILDING', 'ROOM', 'ID NUMBER',
               'PHONE NUMBER', 'ARD', 'CA', 'DR']
    # check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No File Selected'})
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No File Selected'})

    if file and allowed_file(file.filename):
        error_count = 0
        error_values = []

        try:
            students = file.read().decode('utf-8')
            # remove all "" from fields
            students = students.replace('\"', "")
            # getting rid of \n at end of line, to make it compatible with windows and linux
            students = students.replace('\n', "")

            # convert to a list
            students = students.split('\r')

            # move list into a pandas dataframe
            student_df = pd.DataFrame([student.split(',')
                                       for student in students], columns=columns)
            # make an error dataframe to add of the errors to
            error_df = pd.DataFrame()

            student_df = clean_student_data(student_df)
            student_df, error_df = validate_student_data(student_df, error_df)
            student_df, error_df, new_student_count, hall_update_count, room_update_count, new_employee_count, removed_employee_count = update_student_data(
                student_df, error_df)

            if not error_df.empty:
                # get a count of the errors
                error_count = error_df['USERNAME'].count()
                # reorder error_df columns
                error_df = error_df[error_columns]
                # convert df to list so it can be passed to client
                error_values = error_df.values.tolist()
            return jsonify({'new_student_count': new_student_count,
                            'hall_update_count': hall_update_count,
                            'room_update_count': room_update_count,
                            'new_employee_count': new_employee_count,
                            'removed_employee_count': removed_employee_count,
                            'error_count': str(error_count),
                            'error_values': error_values,
                            'error_columns': error_columns})
        except KeyError as err:
            return jsonify({'error': f'csv format error: {str(err)}'})
        except AssertionError as err:
            return jsonify({'error': f'Number of columns error: {str(err)}'})
        except:
            return jsonify({'error': 'An unexpected error occurred'})

    else:
        return jsonify({'error': 'That file type is not supported'})


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
