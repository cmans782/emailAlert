from flask import render_template
from flask_mail import Message
from mailalert import mail, db
from mailalert.models import Employee, Hall, Student, Phone, Utils
from mailalert.employees.utils import generate_random_string, send_reset_password_email
from flask_login import current_user
from functools import wraps
from mailalert.config import Config
from datetime import datetime
import pandas as pd


error_columns = ['USERNAME', 'FIRST NAME', 'LAST NAME',
                 'BUILDING', 'ROOM', 'ID NUMBER', 'PHONE NUMBER',
                 'ARD', 'ALIAS', 'DR', 'ERROR']
building_dict = {}


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
    """
    Change all data in df to the same case
    Remove any special characters from phone number

    Parameters:
        df - Dataframe object of students and employees

    Return:
        df - Dataframe object of students and employees
    """
    df['USERNAME'] = df['USERNAME'].str.lower()
    df['FIRST NAME'] = df['FIRST NAME'].str.title()
    df['LAST NAME'] = df['LAST NAME'].str.title()
    df['BUILDING'] = df['BUILDING'].str.upper()
    df['ROOM'] = df['ROOM'].str.upper()
    df['PHONE NUMBER'] = df['PHONE NUMBER'].replace(
        regex=True, to_replace=r'[-( ).]', value='')
    return df


def validate_student_data(df, error_df):
    """
    validate that all data in df is correct. If a student or
    employee is invalid, remove it from the df and add it to
    error_df

    Parameters:
        df - Dataframe object of students and employees
        error_df - Dataframe object of the students and
                    employees that are invalid

    Return:
        df - Dataframe object of students and employees
        error_df - Dataframe object of the students and
                    employees that are invalid
    """
    # build hall dictionary
    halls = Hall.query.filter_by(active=True)
    for hall in halls:
        building_dict[hall.building_code] = hall.name
    # validate username
    # if username is valid, the row in the result df will be true, if
    # username is invalid the row in the result df will be false
    result = df['USERNAME'].str.contains(r'^[a-z]{4,5}[0-9]{3}$', regex=True)
    # find all of the false rows and add their index to a index_list
    index_list = df[result == False].index.tolist()
    if index_list:
        # get the false row by index and append it to error_df
        error_df = pd.concat([error_df, df.iloc[index_list]], sort=True)
        # add the name of the column where there was an error to the ERROR column
        for index in index_list:
            error_df.at[index, 'ERROR'] = 'USERNAME'
        # create a new df of only usernames that are valid
        df = df[df['USERNAME'].str.contains(r'^[a-z]{5}[0-9]{3}$', regex=True)]
        # reset the index of both df's
        df.reset_index(drop=True, inplace=True)
        error_df.reset_index(drop=True, inplace=True)

    # validate building
    result = df['BUILDING'].str.contains('|'.join(building_dict.keys()))
    # index_list contains invalid rows
    # a building is invalid if it is not in the building_dict
    index_list = df[result == False].index.tolist()
    if index_list:
        error_df = pd.concat([error_df, df.iloc[index_list]], sort=True)
        for index in index_list:
            error_df.at[index, 'ERROR'] = 'NO HALL FOUND'
        df = df[df['BUILDING'].str.contains('|'.join(building_dict.keys()))]
        df.reset_index(drop=True, inplace=True)
        error_df.reset_index(drop=True, inplace=True)

    # validate room
    # a valid room contains 1-3 digits and 0-2 letters denoting the bed
    # eg. 102 B
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
    # a valid ID number contains 6-9 digits only
    result = df['ID NUMBER'].str.contains(r'^[0-9]{6,9}$', regex=True)
    index_list = df[result == False].index.tolist()
    if index_list:
        error_df = pd.concat([error_df, df.iloc[index_list]], sort=True)
        for index in index_list:
            error_df.at[index, 'ERROR'] = 'ID NUMBER'
        df = df[df['ID NUMBER'].str.contains(r'^[0-9]{6,9}$', regex=True)]
        df.reset_index(drop=True, inplace=True)
        error_df.reset_index(drop=True, inplace=True)
    # if id number is not 9 digits long, prepend 0 to it
    # to make all id's 9 digits long
    df['ID NUMBER'] = df['ID NUMBER'].apply(lambda x: str(int(x)).zfill(9))

    # validate phone number. allow empty numbers
    # valid if left empty or has 10-11 digits
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
    """
    Update student and employee information if there are
    any changes. Add any new students or employees. deactive
    any employees if they no longer have the correct employment
    code.

    Parameters:
        df - Dataframe object of students and employees
        error_df - Dataframe object of the students and
                    employees that are invalid

    Return:
        df - Dataframe object of students and employees
        error_df - Dataframe object of the students and
                    employees that are invalid
        new_student_count
        hall_update_count
        room_update_count
        new_employee_count
        removed_employee_count
    """
    students_list = df.values.tolist()
    new_student_count = 0
    hall_update_count = 0
    room_update_count = 0
    new_employee_count = 0
    removed_employee_count = 0

    # build hall dictionary
    halls = Hall.query.filter_by(active=True)
    for hall in halls:
        building_dict[hall.building_code] = hall.name

    # make sure there is an active utility
    utils = Utils.query.filter_by(active=True).first()
    if not utils:
        return -1, -1, -1, -1, -1, -1, -1
    employment_code = utils.employment_code

    for student in students_list:
        email = student[0] + '@live.kutztown.edu'
        existing_employee_hall = None
        new_employee_hall = None
        error = False
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
                student.append('DUPLICATE ID NUMBER')
                temp_df = pd.DataFrame([student], columns=error_columns)
                error_df = pd.concat([error_df, temp_df], sort=True)
                error_df.reset_index(drop=True, inplace=True)
                continue

            new_student = Student(email=email, first_name=student[1], last_name=student[2],
                                  hall=hall_obj, room_number=student[4], student_id=student[5])

            # check if the student goes by a different name
            if len(student[8].strip()):
                new_student.first_name = student[8].title()

            # if phone number is not empty add it to db
            if student[6] != '':
                phone_number = Phone(phone_number=student[6])
                new_student.phone_numbers.append(phone_number)
                db.session.add(phone_number)

            db.session.add(new_student)
            new_student_count += 1

        # check if the student is an existing employee
        if employee_obj:
            if len(student[9].strip()):
                # validat employee code
                existing_employee_hall, _ = validate_Employee(
                    student[9], employment_code)

            # check if the employee has the current employment code
            if student[7] == employment_code or existing_employee_hall:
                # give the employee the correct access
                employee_obj.access = 'Building Director' if student[7] == employment_code else 'DR'
                # check if the employee was deactivated but is now activated
                if employee_obj.active == False:
                    password = generate_random_string()
                    employee_obj.active = True
                    employee_obj.end_date = None
                    employee_obj.reset_password = True
                    employee_obj.password = password
                    new_employee_count += 1
                    send_reset_password_email(employee_obj, password)

            # check if the employee was removed from building director position
            elif employee_obj.active == True and employee_obj.access == 'Building Director' and student[7] != employment_code:
                employee_obj.end_date = datetime.utcnow()  # record employees end date
                employee_obj.active = False
                removed_employee_count += 1
            # check if employee was removed from DR position
            if employee_obj.active == True and employee_obj.access == 'DR' and not existing_employee_hall:
                employee_obj.end_date = datetime.utcnow()  # record employees end date
                employee_obj.active = False
                removed_employee_count += 1
            # check if the employee goes by a different name
            if len(student[8].strip()) and student[8] != employee_obj.first_name:
                employee_obj.first_name = student[8].title()
            # check if a the employee went by a different name but does not anymore
            if student[8].strip() == '' and student[1] != employee_obj.first_name:
                employee_obj.first_name = student[1]

        # check if the student is a new Building Director
        elif student[7] == employment_code:
            access = 'Building Director'
            new_employee_hall = building_dict.get(student[3])

        # check if the student is a new DR
        elif len(student[9].strip()):
            new_employee_hall, error = validate_Employee(
                student[9], employment_code)
            access = 'DR'

        # check if there was an error with the employment code
        if error:
            student.append('INVALID EMPLOYMENT CODE')
            temp_df = pd.DataFrame([student], columns=error_columns)
            error_df = pd.concat([error_df, temp_df], sort=True)
            error_df.reset_index(drop=True, inplace=True)
            continue

        # new_employee_hall will only have a value if the employee is either
        # a DR or Building director with a correct hall
        if new_employee_hall:
            hall_obj = Hall.query.filter_by(name=new_employee_hall).first()
            password = generate_random_string()
            new_employee = Employee(email=email, first_name=student[1],
                                    last_name=student[2], access=access,
                                    hall=hall_obj, password=password)

            # check if the employee goes by a different name
            if len(student[8].strip()):
                new_employee.first_name = student[8].title()

            new_employee_count += 1
            send_reset_password_email(new_employee, password)
            db.session.add(new_employee)
    db.session.commit()
    return df, error_df, new_student_count, hall_update_count, room_update_count, new_employee_count, removed_employee_count


def is_active(df):
    """
    validate that a student is still active. If the student
    is no longer in the csv file being uploaded, they are
    marked as inactive. If the student is also an employee,
    mark them as inactive as well.

    Parameters:
        df - Dataframe object of students and employees

    Return:
        deactivate_count - number of students deactivated
    """
    deactivate_count = 0
    # students in csv being uploaded
    student_id_list = df['ID NUMBER'].values.tolist()
    current_students = Student.query.all()
    for student in current_students:
        # if the student is no longer in the csv file, deactivate them
        if student.active == True and not student.student_id in student_id_list:
            student.active = False
            student.end_date = datetime.utcnow()
            deactivate_count += 1
            # if the student is also a DR, deactive them as well
            employee = Employee.query.filter_by(
                email=student.email, access='DR').first()
            if employee:
                employee.end_date = datetime.utcnow()  # record employees end date
                employee.active = False
        # check if the student was deactivated but is now active
        elif student.active == False and student.student_id in student_id_list:
            student.active = True
            student.start_date = datetime.utcnow()
            student.end_date = None
    db.session.commit()
    return deactivate_count


def validate_Employee(student_code, employment_code):
    """
    Make sure the DR is valid. first make sure they
    have the employment code, then see if they have
    a building key in their code.

    Parameters:
        student_code - contains students employment code and working hall
        employment_code - current code for all valid employees

    Return:
        DR's working hall if valid, None if not valid 
    """
    # check if the employment code is in student code
    if employment_code not in student_code:
        return None, True
    # iterate through all the keys in the building_dict
    # to see if the buildiing code is in the student code
    for key, _ in building_dict.items():
        if key in student_code.upper():
            return building_dict.get(key), False
    return None, True
