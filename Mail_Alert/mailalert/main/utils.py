from flask import url_for, redirect, render_template
from flask_mail import Message
from mailalert import mail, db
from mailalert.models import Employee, Hall, Student, Phone
from mailalert.employees.utils import generate_random_string, send_reset_password_email
from flask_login import current_user
from functools import wraps
from mailalert.config import Config
from datetime import datetime
import pandas as pd


error_columns = ['USERNAME', 'FIRST NAME', 'LAST NAME',
                 'BUILDING', 'ROOM', 'ID NUMBER',
                 'PHONE NUMBER', 'ERROR']


def send_package_update_email(message, recipients, cc_recipients):
    msg = Message()
    msg.subject = 'Package Update'
    msg.sender = 'KutztownMail@gmail.com'
    msg.recipients = [recipients]
    msg.cc = [cc_recipients]
    msg.body = message

    mail.send(msg)


def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.allowed(access_level):
                return render_template('errors/403.html')
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def clean_student_data(df):
    df['USERNAME'] = df['USERNAME'].str.lower()
    df['FIRST NAME'] = df['FIRST NAME'].str.title()
    df['LAST NAME'] = df['LAST NAME'].str.title()
    df['BUILDING'] = df['BUILDING'].str.upper()
    df['ROOM'] = df['ROOM'].str.upper()
    df['PHONE NUMBER'] = df['PHONE NUMBER'].replace(
        regex=True, to_replace=r'[-( ).]', value='')
    return df


def validate_student_data(df, error_df):
    building_dict = {}
    halls = Hall.query.all()
    # build hall dictionary
    for hall in halls:
        building_dict[hall.building_code] = hall.name

    # if username is correct, the row in the result df will be true, otherwise false
    result = df['USERNAME'].str.contains(r'^[a-z]{4,5}[0-9]{3}$', regex=True)
    # add the index of all the false rows to a list
    index_list = df[result == False].index.tolist()
    if index_list:
        # get the false row by index and append it to error_df
        error_df = pd.concat([error_df, df.iloc[index_list]], sort=True)
        # add the name of the column where there was an error to the ERROR column
        for index in index_list:
            error_df.at[index, 'ERROR'] = 'USERNAME'
        # remove the students that had errors from df
        df = df[df['USERNAME'].str.contains(r'^[a-z]{5}[0-9]{3}$', regex=True)]
        # reset the index after removing rows
        df.reset_index(drop=True, inplace=True)
        error_df.reset_index(drop=True, inplace=True)

    # validate building
    result = df['BUILDING'].str.contains('|'.join(building_dict.keys()))
    index_list = df[result == False].index.tolist()
    if index_list:
        error_df = pd.concat([error_df, df.iloc[index_list]], sort=True)
        for index in index_list:
            error_df.at[index, 'ERROR'] = 'NO HALL FOUND'
        df = df[df['BUILDING'].str.contains('|'.join(building_dict.keys()))]
        df.reset_index(drop=True, inplace=True)
        error_df.reset_index(drop=True, inplace=True)

    # validate room
    result = df['ROOM'].str.contains(r'^[0-9]{1,3}[A-Z]{0,2}$', regex=True)
    index_list = df[result == False].index.tolist()
    if index_list:
        error_df = pd.concat([error_df, df.iloc[index_list]], sort=True)
        for index in index_list:
            error_df.at[index, 'ERROR'] = 'ROOM'
        df = df[df['ROOM'].str.contains(r'^[0-9]{1,3}[A-Z]{0,2}$', regex=True)]
        df.reset_index(drop=True, inplace=True)
        error_df.reset_index(drop=True, inplace=True)

    # validate id number
    result = df['ID NUMBER'].str.contains(r'^[0-9]{6,9}$', regex=True)
    index_list = df[result == False].index.tolist()
    if index_list:
        error_df = pd.concat([error_df, df.iloc[index_list]], sort=True)
        for index in index_list:
            error_df.at[index, 'ERROR'] = 'ID NUMBER'
        df = df[df['ID NUMBER'].str.contains(r'^[0-9]{6,9}$', regex=True)]
        df.reset_index(drop=True, inplace=True)
        error_df.reset_index(drop=True, inplace=True)
    # prepend 0 to id number to make all id's 9 digits long
    df['ID NUMBER'] = df['ID NUMBER'].apply(lambda x: str(int(x)).zfill(9))

    # validate phone number allow empty numbers
    result = df['PHONE NUMBER'].str.contains(
        r'^[0-9]{0}$|^[0-9]{10,11}$', regex=True)
    index_list = df[result == False].index.tolist()
    if index_list:
        error_df = pd.concat([error_df, df.iloc[index_list]], sort=True)
        for index in index_list:
            error_df.at[index, 'ERROR'] = 'PHONE NUMBER'
        df = df[df['PHONE NUMBER'].str.contains(
            r'^[0-9]{0}$|^[0-9]{10}$', regex=True)]
        df.reset_index(drop=True, inplace=True)
        error_df.reset_index(drop=True, inplace=True)

    return df, error_df


def update_student_data(df, error_df):
    students_list = df.values.tolist()
    new_student_count = 0
    hall_update_count = 0
    room_update_count = 0
    new_employee_count = 0
    removed_employee_count = 0
    employment_code = '2198'
    roth_employment_code = '2198 RT'

    building_dict = {}
    halls = Hall.query.all()
    # build hall dictionary
    for hall in halls:
        building_dict[hall.building_code] = hall.name

    # for now just hardcode the hall the we are running in
    # will have to change if this goes campus wide
    roth_hall_obj = Hall.query.filter_by(name='Rothermel').first()

    for student in students_list:
        email = student[0] + '@live.kutztown.edu'
        student_obj = Student.query.filter_by(email=email).first()
        employee_obj = Employee.query.filter_by(email=email).first()
        hall_obj = Hall.query.filter_by(
            name=building_dict.get(student[3])).first()
        if student_obj:
            # update student hall
            if student_obj.hall != hall_obj:
                student_obj.hall = hall_obj
                hall_update_count += 1
            # update student room number
            if student_obj.room_number != student[4]:
                student_obj.room_number = student[4]
                room_update_count += 1
            # update student first name
            student_obj.first_name = student[1].title()
            # update student last name
            student_obj.last_name = student[2].title()

            # check if the student goes by a different name
            if len(student[8].strip()):
                student_obj.first_name = student[8].title()
            # check if a student went by a different name but does not anymore
            if student[8].strip() == '':
                student_obj.first_name = student[1]

        # if student does not exist make a new student
        else:
            student_id_exists = Student.query.filter_by(
                student_id=student[5]).first()
            # if a student already has this id add it to the error_df
            if student_id_exists:
                del student[9]
                del student[8]
                student[7] = 'DUPLICATE ID NUMBER'
                temp_df = pd.DataFrame([student], columns=error_columns)
                error_df = pd.concat([error_df, temp_df], sort=True)
                error_df.reset_index(drop=True, inplace=True)
                continue

            new_student = Student(email=email, first_name=student[1], last_name=student[2],
                                  hall=hall_obj, room_number=student[4], student_id=student[5])

            # check if the student goes by a different name
            if len(student[8].strip()):
                new_student.first_name = student[8].title()

            db.session.add(new_student)
            # if phone number is not empty add it to db
            if student[6] != '':
                phone_number = Phone(phone_number=student[6])
                new_student.phone_numbers.append(phone_number)
                db.session.add(phone_number)
            new_student_count += 1

        # check if the student is an existing employee
        if employee_obj:
            password = generate_random_string()
            # check if the employee has the current employment code
            if student[7] == employment_code or student[9] == roth_employment_code:
                # give the student the correct access
                employee_obj.access = 'Building Director' if student[7] == employment_code else 'DR'
                employee_obj.hall = roth_hall_obj
                # check if the employee was deactivated
                if employee_obj.active == False:
                    employee_obj.active = True
                    employee_obj.end_date = None
                    employee_obj.reset_password = True
                    employee_obj.password = password
                    new_employee_count += 1
                    ######### uncomment before releasing #########
                    send_reset_password_email(employee_obj, password)

            # check if the employee was removed from building director position
            elif employee_obj.access == 'Building Director' and student[7] != employment_code:
                employee_obj.end_date = datetime.now()  # record employees end date
                employee_obj.active = False
                employee_obj.access = 'None'
                removed_employee_count += 1
            # check if employee was removed from DR position
            if employee_obj.access == 'DR' and student[9] != roth_employment_code:
                employee_obj.end_date = datetime.now()  # record employees end date
                employee_obj.active = False
                employee_obj.access = 'None'
                removed_employee_count += 1
            # check if the student goes by a different name
            if len(student[8].strip()) and student[8] != employee_obj.first_name:
                employee_obj.first_name = student[8].title()
            # check if a student went by a different name but does not anymore
            if student[8].strip() == '' and student[1] != employee_obj.first_name:
                employee_obj.first_name = student[1]

        # check if the student is a new employee
        elif student[7] == employment_code or student[9] == roth_employment_code:
            password = generate_random_string()
            access = 'Building Director' if student[7] == employment_code else 'DR'

            new_employee = Employee(email=email, first_name=student[1],
                                    last_name=student[2], access=access,
                                    hall=roth_hall_obj, password=password)

            # check if the employee goes by a different name
            if len(student[8].strip()):
                new_employee.first_name = student[8].title()

            new_employee_count += 1
            ######### uncomment before releasing #########
            send_reset_password_email(new_employee, password)
            db.session.add(new_employee)
    db.session.commit()
    return df, error_df, new_student_count, hall_update_count, room_update_count, new_employee_count, removed_employee_count
