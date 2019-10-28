from flask import url_for, flash
from flask_mail import Message
from mailalert import mail, bcrypt, db
from sqlalchemy import event
from mailalert.models import Employee, Student, Hall, Phone
import string
from random import choice, randint
import pandas as pd
import numpy as np
from datetime import datetime


column_names = ['USERNAME', 'FIRST NAME', 'LAST NAME',
                'BUILDING', 'ROOM', 'ID NUMBER',
                'PHONE NUMBER', 'ERROR', 'ARD', 'DR']


def send_reset_email(employee):
    token = employee.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='KutztownMail@gmail.com', recipients=[employee.email])
    msg.body = f"""To reset your password, visit the following link:
{url_for('employees.reset_token', token=token, _external=True)}

If you did not make this request then please ignore this email.
"""

    mail.send(msg)


def generate_random_string():
    min_char = 8
    max_char = 12
    allchar = string.ascii_letters + string.punctuation + string.digits
    password = "".join(choice(allchar)
                       for x in range(randint(min_char, max_char)))
    return password


def send_reset_password_email(employee, password):
    msg = Message('Temporary Password', sender='KutztownMail@gmail.com',
                  recipients=[employee.email])
    msg.body = f"""You have just been added to the Kutztown Mail Alert team! 
Your temporary password is:

{password}

In order to login, you must first reset your password
To reset your password, visit the following link:
{url_for('employees.reset_password', _external=True)}

if you did not make this request then please ignore this email.
"""
    mail.send(msg)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@event.listens_for(Employee.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    if value != oldvalue:
        return bcrypt.generate_password_hash(value).decode(
            'utf-8')
    return value


def clean_student_data(df):
    df['USERNAME'] = df['USERNAME'].str.lower()
    df['FIRST NAME'] = df['FIRST NAME'].str.capitalize()
    df['LAST NAME'] = df['LAST NAME'].str.capitalize()
    df['BUILDING'] = df['BUILDING'].str.upper()
    df['ROOM'] = df['ROOM'].str.upper()
    # if id number is only 7 characters long, prepend 00 to it
    df.loc[df["ID NUMBER"].str.len() == 7, ['ID NUMBER']] = '00' + \
        df['ID NUMBER'].astype(str)
    df['PHONE NUMBER'] = df['PHONE NUMBER'].replace(
        regex=True, to_replace=r'[-( )]', value='')
    # remove any non digit values from ARD and DR
    df['ARD'].replace(regex=True, inplace=True, to_replace=r'\D', value=r'')
    df['DR'].replace(regex=True, inplace=True, to_replace=r'\D', value=r'')
    return df


def validate_student_data(df, error_df):
    building_dict = {}
    halls = Hall.query.all()
    # build hall dictionary
    for hall in halls:
        building_dict[hall.building_code] = hall.name

    # if username is correct, the row in the result df will be true, otherwise false
    result = df['USERNAME'].str.contains(r'^[a-z]{5}[0-9]{3}$', regex=True)
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
    result = df['ID NUMBER'].str.contains(r'^[0-9]{9}$', regex=True)
    index_list = df[result == False].index.tolist()
    if index_list:
        error_df = pd.concat([error_df, df.iloc[index_list]], sort=True)
        for index in index_list:
            error_df.at[index, 'ERROR'] = 'ID NUMBER'
        df = df[df['ID NUMBER'].str.contains(r'^[0-9]{9}$', regex=True)]
        df.reset_index(drop=True, inplace=True)
        error_df.reset_index(drop=True, inplace=True)

    # validate phone number allow empty numbers
    result = df['PHONE NUMBER'].str.contains(
        r'^[0-9]{0}$|^[0-9]{10}$', regex=True)
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

    building_dict = {}
    halls = Hall.query.all()
    # build hall dictionary
    for hall in halls:
        building_dict[hall.building_code] = hall.name

    for student in students_list:
        email = student[0] + '@live.kutztown.edu'
        student_obj = Student.query.filter_by(email=email).first()
        employee_obj = Employee.query.filter_by(email=email).first()
        hall_obj = Hall.query.filter_by(
            name=building_dict.get(student[3])).first()
        # update student hall and room number
        if student_obj:
            if student_obj.hall != hall_obj:
                student_obj.hall = hall_obj
                hall_update_count += 1
            if student_obj.room_number != student[4]:
                room_number_exists = Student.query.filter_by(
                    room_number=student[4], hall=hall_obj).first()
                # if a student already has this id add it to the error_df
                if room_number_exists:
                    student.append('DUPLICATE ROOM NUMBER')
                    temp_df = pd.DataFrame([student], columns=column_names)
                    error_df = pd.concat([error_df, temp_df], sort=True)
                    error_df.reset_index(drop=True, inplace=True)
                    continue
                else:
                    student_obj.room_number = student[4]
                    room_update_count += 1

        # if student does not exist make a new student
        else:
            room_number_exists = Student.query.filter_by(
                room_number=student[4], hall=hall_obj).first()
            # if a student already has this id add it to the error_df
            if room_number_exists:
                student.append('DUPLICATE ROOM NUMBER')
                temp_df = pd.DataFrame([student], columns=column_names)
                error_df = pd.concat([error_df, temp_df], sort=True)
                error_df.reset_index(drop=True, inplace=True)
                continue

            student_id_exists = Student.query.filter_by(
                student_id=student[5]).first()
            # if a student already has this id add it to the error_df
            if student_id_exists:
                student.append('DUPLICATE ID NUMBER')
                temp_df = pd.DataFrame([student], columns=column_names)
                error_df = pd.concat([error_df, temp_df], sort=True)
                error_df.reset_index(drop=True, inplace=True)
                continue

            new_student = Student(email=email, first_name=student[1], last_name=student[2],
                                  hall=hall_obj, room_number=student[4], student_id=student[5])
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
            if student[7] == employment_code or student[8] == employment_code:
                # give the student the correct access
                employee_obj.access = 'Building Director' if student[7] else 'DR'
                employee_obj.hall = hall_obj
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
                removed_employee_count += 1
            # check if employee was removed from DR position
            elif employee_obj.access == 'DR' and student[8] != employment_code:
                employee_obj.end_date = datetime.now()  # record employees end date
                employee_obj.active = False
                removed_employee_count += 1
        # check if the student is a new employee
        elif student[7] == employment_code or student[8] == employment_code:
            password = generate_random_string()
            # if the code is in the ARD column, make the employee an ARD
            if student[7]:
                new_employee = Employee(email=email, first_name=student[1],
                                        last_name=student[2], access='Building Director',
                                        hall=hall_obj, password=password)
            # if the code is in the DR column, make the employee a DR
            if student[8]:
                new_employee = Employee(email=email, first_name=student[1],
                                        last_name=student[2], access='DR',
                                        hall=hall_obj, password=password)
            new_employee_count += 1
            ######### uncomment before releasing #########
            send_reset_password_email(new_employee, password)
            db.session.add(new_employee)
    db.session.commit()
    return df, error_df, new_student_count, hall_update_count, room_update_count, new_employee_count, removed_employee_count
