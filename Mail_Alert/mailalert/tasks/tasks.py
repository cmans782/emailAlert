from mailalert.main.utils import clean_student_data, validate_student_data, \
    update_student_data, is_active, error_columns
from mailalert.tasks.utils import send_err_email
from requests.exceptions import HTTPError
from mailalert.models import Task
from mailalert import db
from datetime import datetime
from flask import jsonify, Blueprint
from mailalert import celery
import requests
import pandas as pd


class Error(Exception):
    """Base class for other exceptions"""
    pass


class EmploymentCodeError(Error):
    """Raised when there is no active employment code"""
    pass


@celery.task(name='tasks.update_students')
def update_students():
    columns = ['USERNAME', 'FIRST NAME', 'LAST NAME',
               'BUILDING', 'ROOM', 'ID NUMBER',
               'PHONE NUMBER', 'ARD', 'ALIAS', 'DR']
    error_count = 0
    error_values = []
    status = 'SUCCESS'
    err_msg = ''

    try:
        r = requests.get('http://3.86.235.138:5000/students')
        r.raise_for_status()
        students = r.json()  # convert response to a dict

        student_df = pd.DataFrame(students)  # make pandas dataframe
        # make columns upper case
        student_df.columns = map(str.upper, student_df.columns)
        student_df = student_df[columns]  # reorder columns

        # replace None values with empty string
        mask = student_df.applymap(lambda x: x is None)
        cols = student_df.columns[(mask).any()]
        for col in student_df[cols]:
            student_df.loc[mask[col], col] = ''

        error_df = pd.DataFrame()  # make an error df

        student_df = clean_student_data(student_df)
        student_df, error_df = validate_student_data(student_df, error_df)
        student_df, error_df, new_student_count, hall_update_count, room_update_count, new_employee_count, removed_employee_count = update_student_data(
            student_df, error_df)

        if new_student_count == -1:
            raise EmploymentCodeError

        deactived_students_count = is_active(student_df)

        # check if there were any errors
        if not error_df.empty:
            error_count = error_df['USERNAME'].count()
            # reorder error_df columns
            error_df = error_df[error_columns]
            # convert df to list so it can be passed to client
            error_values = error_df.values.tolist()
            err_msg = '1 or more students failed to upload'
            status = 'ERROR'

    except HTTPError as http_err:
        err_msg = f'HTTP error occurred: {str(http_err)}'
        status = 'FAILED'
    except KeyError as err:
        err_msg = f'csv format error: {str(err)}'
        status = 'FAILED'
    except AssertionError as err:
        err_msg = f'Number of columns error: {str(err)}'
        status = 'FAILED'
    except EmploymentCodeError:
        err_msg = 'No active employment code'
        status = 'FAILED'
    except Exception as err:
        err_msg = f'An unexpected error occurred: {str(err)}'
        status = 'FAILED'

    finally:
        time = datetime.now()
        task = Task(name='Roster Upload', status=status,
                    message=err_msg, date_done=time)
        db.session.add(task)
        db.session.commit()
        if err_msg:
            send_err_email(status, err_msg, time, error_df)
            return jsonify({'error': err_msg})
        else:
            return jsonify({'new_student_count': new_student_count,
                            'hall_update_count': hall_update_count,
                            'room_update_count': room_update_count,
                            'new_employee_count': new_employee_count,
                            'removed_employee_count': removed_employee_count,
                            'deactived_students_count': deactived_students_count,
                            'error_count': str(error_count),
                            'error_values': error_values,
                            'error_columns': error_columns})
