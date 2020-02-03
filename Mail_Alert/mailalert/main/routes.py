import os
import csv
import json
import pandas as pd
from jira import JIRA
from mailalert import db
from flask import render_template, Blueprint, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from mailalert.main.forms import ComposeEmailForm, CreateMessageForm, NewIssueForm
from mailalert.models import SentMail, Student, Hall, Utils
from mailalert.main.utils import clean_student_data, validate_student_data, \
    update_student_data, error_columns, allowed_file, is_active

main = Blueprint('main', __name__)


@main.route("/get_halls", methods=['GET'])
def get_halls():
    """
    get all of the halls in the database

    Return: 
        JSON object of all the halls to ajax request
    """
    hall_list = Hall.query.filter_by(active=True)
    hall_list = [hall.name for hall in hall_list]
    # remove the current users hall because it is already being displayed
    hall_list.remove(current_user.hall.name)
    return jsonify({'halls': hall_list})


@main.route("/change_working_hall", methods=['POST'])
@login_required
def change_working_hall():
    """
    Change the current users working hall 

    Return: 
        JSON to ajax request
        "success" if hall was successfully changed
        "error" if the hall being changed to does not
        exist
    """
    new_hall = request.form.get('new_hall', None)
    hall = Hall.query.filter_by(name=new_hall, active=True).first()
    if hall:
        current_user.hall = hall
        db.session.commit()
    else:
        flash(f'Error changing to {new_hall}', 'danger')
    return jsonify({'success': 'success'})


@main.route("/upload_csv", methods=['POST'])
@login_required
def upload_csv():
    """
    Update student and employee database with most recent 
    information via csv upload. Create error csv file with 
    any students or employees that failed to upload 

    Return: 
        JSON to ajax request
        on success -
            new_student_count
            hall_update_count
            room_update_count
            new_employee_count 
            removed_employee_count
            error_count
            error_values - all of the errors in a list
            error_columns - the column names of the errors
        on error -
            json object with appropriate error message
    """
    columns = ['USERNAME', 'FIRST NAME', 'LAST NAME',
               'BUILDING', 'ROOM', 'ID NUMBER',
               'PHONE NUMBER', 'ARD', 'ALIAS', 'DR']

    # check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No File Selected'})
    # get the file the user selected
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No File Selected'})

    if file and allowed_file(file.filename):
        error_count = 0
        error_values = []

        try:
            students = file.read().decode('utf-8')
            # check if file is empty
            if not students:
                return jsonify({'error': 'File is Empty'})
            # remove all "" from fields
            students = students.replace('\"', "")
            # getting rid of \n at end of line, to make it compatible with windows and linux
            students = students.replace('\n', "")
            # split on return character and make into list
            students = students.split('\r')
            # move list into a pandas dataframe
            student_df = pd.DataFrame([student.split(',')
                                       for student in students], columns=columns)
            # make an error dataframe to add errors to
            error_df = pd.DataFrame()

            student_df = clean_student_data(student_df)
            student_df, error_df = validate_student_data(student_df, error_df)
            student_df, error_df, new_student_count, hall_update_count, room_update_count, new_employee_count, removed_employee_count = update_student_data(
                student_df, error_df)
            if new_student_count == -1:
                return jsonify({'error': 'You must set an active employment code before adding students or employees'})
            deactived_students_count = is_active(student_df)

            # check if there were any errors
            if not error_df.empty:
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
                            'deactived_students_count': deactived_students_count,
                            'error_count': str(error_count),
                            'error_values': error_values,
                            'error_columns': error_columns})
        except KeyError as err:
            return jsonify({'error': f'csv format error: {str(err)}'})
        except AssertionError as err:
            return jsonify({'error': f'Number of columns error: {str(err)}'})
        except Exception as err:
            return jsonify({'error': f'An unexpected error occurred: {str(err)}'})
    else:
        return jsonify({'error': 'That file type is not supported'})


@main.route("/feedback", methods=['GET', 'POST'])
@login_required
def feedback():
    """
    recieve bugs new feature requests reported by users
    and send them to Jira  

    Return: 
        render feedback.html
    """
    form = NewIssueForm()
    if form.validate_on_submit():
        options = {'server': 'https://mailalert.atlassian.net'}
        jira = JIRA(options, basic_auth=('corey2232@gmail.com',
                                         'sIcygfuR6RqdHbbnsziT5C0D'))
        jira.create_issue(project='MA', summary=form.summary.data, description=form.description.data,
                          priority={'name': form.priority.data}, issuetype={'name': form.issueType.data})

        flash(f'Your feedback has been sent to the development team!', 'success')
        return redirect(url_for('main.feedback'))
    return render_template('feedback.html', title='Feedback', form=form)
