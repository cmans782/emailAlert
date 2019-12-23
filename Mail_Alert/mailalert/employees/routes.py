from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify, session
from flask_login import login_user, current_user, logout_user, login_required
from mailalert import db, bcrypt
from mailalert.models import Employee, Hall, Login, Student
from mailalert.employees.forms import ManagementForm, LoginForm, RequestResetForm, ResetPasswordForm, NewPasswordForm, NewHallForm
from mailalert.employees.utils import send_reset_email, send_reset_password_email, generate_random_string
from mailalert.main.utils import requires_access_level
from sqlalchemy import func
from datetime import datetime
import json
import re

employees = Blueprint('employees', __name__)


@employees.route("/management", methods=['GET', 'POST'])
@login_required
@requires_access_level('Building Director')
def management():
    """
    renders management.html page as well as handles adding new employees and halls 

    GET - 
        returns all the halls
    POST - 
        form.validate_on_submit() - will add a new employee if the employee does not yet exist 
        new_hall_form.validate_on_submit - will add a new hall if the hall does not yet exist

    Returns: 
        management.html 
    """
    form = ManagementForm()
    new_hall_form = NewHallForm()
    # get all active halls and add them to the list of choices
    # for the halls dropdown when adding a new employee
    halls = Hall.query.filter_by(active=True)
    form.hall.choices = [(hall.id, hall.name) for hall in halls]

    # if the user is a Building director and they are adding
    # a new employee, the employee will always be a DR by default
    if form.submit.data and not current_user.is_admin():
        form.role.data = "DR"

    if form.validate_on_submit():
        existing_employee = Employee.query.filter_by(
            email=form.email.data).first()
        if existing_employee:
            flash(
                f'{existing_employee.first_name}\'s account already exists', 'success')
        else:
            password = generate_random_string()
            hall = Hall.query.get(form.hall.data)  # get hall object
            employee = Employee(email=form.email.data, first_name=form.firstName.data.title(),
                                last_name=form.lastName.data.title(), access=form.role.data,
                                hall=hall, password=password)
            flash(f'Account created for {employee.email}!', 'success')
            send_reset_password_email(employee, password)
            db.session.add(employee)
        db.session.commit()
    elif new_hall_form.submit.data and new_hall_form.validate_on_submit():
        hall = new_hall_form.hall.data
        existing_hall = Hall.query.filter_by(name=hall).first()
        if existing_hall:
            flash('This hall already exists', 'danger')
        else:
            building_code = new_hall_form.building_code.data
            hall = Hall(name=hall, building_code=building_code.upper())
            db.session.add(hall)
            db.session.commit()

    # only add certain employees to employees list based on the current users access
    # if the user is not an admin, only get employees that are DR's
    if not current_user.is_admin():
        employees = Employee.query.filter_by(
            access='DR', hall=current_user.hall).all()
    else:
        # user is admin so get all the employees
        employees = Employee.query.all()
    return render_template('management.html', title='Management', form=form, employees=employees, halls=halls, new_hall_form=new_hall_form)


@employees.route("/management/remove_hall", methods=['POST'])
@login_required
def remove_hall():
    """
    Removes a hall if no students or employees live there 

    Returns: 
        JSON response to ajax
        "success" if hall was successfully removed
        "error" if hall could not be removed 
    """
    hall_id = request.form.get('hall_id', None)
    hall = Hall.query.get(hall_id)
    if hall:
        student = Student.query.filter_by(hall=hall, active=True).first()
        if student:
            return jsonify({'error': f'{hall.name} cannot be removed if a student lives in that hall'})
        employee = Employee.query.filter_by(hall=hall, active=True).first()
        if employee:
            return jsonify({'error': f'{hall.name} cannot be removed if an employee works in that hall'})

        hall.active = False
        hall.end_date = datetime.now()

        db.session.commit()
        return jsonify({'success': 'success'})
    else:
        return jsonify({'error': 'Could not find that hall'})


@employees.route("/management/validate", methods=['POST'])
@login_required
def _validate():
    """
    Validate new employee information 
    Validate new hall information

    email - make sure no other employees have that email
    hall name- make sure the hall entered does not yet exist
    building code - make sure the building code entered does 
                    not yet exist

    Returns: 
        JSON response to ajax
        "success" if hall, building code or email do not yet exist
        "error" if hall, building code, or email do exist
    """
    email = request.form.get('email', None)
    hall = request.form.get('hall', None)
    building_code = request.form.get('building_code', None)
    if email:
        # check if email entered is valid
        if not re.search('^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email):
            return jsonify({'error': 'Invalid email'})
        user = Employee.query.filter_by(email=email).first()
        # check if that email is already in use
        if user:
            return jsonify({'error': 'This email is already in use'})
    elif hall:
        # search for existing hall case insensitive
        hall = Hall.query.filter(func.lower(
            Hall.name) == func.lower(hall)).first()
        if hall:
            return jsonify({'hall_error': 'This hall already exists'})
    elif building_code:
        hall = Hall.query.filter_by(
            building_code=building_code.upper()).first()
        if hall:
            return jsonify({'bcode_error': 'This building code already exitsts'})
    return jsonify({'success': 'success'})


@employees.route("/management/activate", methods=['POST'])
@login_required
def _activate_employee():
    """
    Reactivate an inactive employee

    Returns: 
        "success" JSON response to ajax
    """
    employee_id_list = request.json
    if employee_id_list:
        for employee_id in employee_id_list:
            employee = Employee.query.filter_by(id=employee_id).first()
            if employee.active == True:
                continue
            employee.active = True
            employee.end_date = None
            employee.reset_password = True
            employee.start_date = datetime.now()
            password = generate_random_string()
            employee.password = password
            send_reset_password_email(employee, password)
            flash(f'{employee.first_name}\'s account has been reactivated', 'success')
        db.session.commit()
    else:
        flash('No employees were selected', 'danger')
    return jsonify({'success': 'success'})


@employees.route("/management/deactivate", methods=['POST'])
@login_required
def deactivate_employee():
    """
    deactivate an employee

    Returns: 
        redirect to management route
    """
    employee_id_list = request.form.getlist("employee_checkbox")
    if employee_id_list:  # make sure the user selected at least one employee
        for employee_id in employee_id_list:
            # get the employee object using its id
            employee = Employee.query.get(employee_id)
            employee.end_date = datetime.now()  # record employees end date
            employee.active = False
            flash(f'{employee.first_name}\'s account has been deactivated', 'success')
        db.session.commit()
    else:
        flash('No employees were selected', 'danger')
    return redirect(url_for('employees.management'))


@employees.route("/", methods=['GET', 'POST'])
@employees.route("/login", methods=['GET', 'POST'])
def login():
    """
    Login an employee

    Returns: 
        GET - 
            renders login.html
        POST -
            redirect for password reset if password has not yet been reset 
            redirect for home route on success
    """
    # check if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('packages.home'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        # check if user enterd full email
        employee = Employee.query.filter_by(email=email).first()
        # check if user just entered username
        if not employee:
            employee = Employee.query.filter_by(
                email=email + '@live.kutztown.edu').first()

        if employee and not employee.active:
            flash(
                'Login Unsuccessful. Management has removed you from the list of active employees', 'danger')

        # check that employee exists and that password entered matches password hash
        elif employee and bcrypt.check_password_hash(employee.password, form.password.data):
            # check if the user still needs to reset their password
            if employee.reset_password:
                flash('Please reset your password before logging in', 'info')
                return redirect(url_for('employees.reset_password'))
            login_user(employee)
            # set their session to permanent once logged in
            session.permanent = True
            # log when user logs in
            login = Login(login_date=datetime.now(), employee=current_user)
            db.session.add(login)
            db.session.commit()
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('packages.home'))
        else:
            flash('Login Unsuccessful. Check email and Password', 'danger')
    return render_template('login.html', title='Login', form=form)


@employees.route("/logout")
def logout():
    """
    Logout an employee

    Returns: 
        redirect to login route
    """
    # get the last login date by the current user and log logout date and time
    current_user.logins[-1].logout_date = datetime.now()
    db.session.commit()
    logout_user()
    return redirect(url_for('employees.login'))


@employees.route("/forgot_password", methods=['GET', 'POST'])
def reset_request():
    """
    send an email to user to reset passowrd

    Returns: 
        GET - 
            renders reset_request.html
        POST - 
            redirect to login route
    """
    # check if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('packages.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(email=form.email.data).first()
        send_reset_email(employee)
        flash(
            f'An email has been sent to {employee.email} with instructions to reset your password.', 'info')
        return redirect(url_for('employees.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@employees.route("/forgot_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    """
    reset the users password if the password was forgotten

    Returns: 
        GET - 
            render reset_token.html
        POST - 
            if expired token redirect to reset_request route
            if password reset was successful redirect to 
            login route 
    """
    # check if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('packages.home'))
    # get employee associated with reset token
    employee = Employee.verify_reset_token(token)
    if employee is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('employees.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        employee.password = form.new_password.data
        employee.reset_password = False
        db.session.commit()
        flash('Your password has been reset!', 'success')
        return redirect(url_for('employees.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@employees.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    """
    Reset a users password while the user is logged in

    Returns: 
        GET - 
            render reset_password.html
        POST -
            redirect to login route on success
            render reset_password.html if not valid 
    """
    form = NewPasswordForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(email=form.email.data).first()
        # check that employee exists and that old password entered matches old password hash
        if employee and bcrypt.check_password_hash(employee.password, form.old_password.data):
            employee.password = form.new_password.data
            employee.reset_password = False
            db.session.commit()
            flash('Your password has been changed!', 'success')
            login_user(employee)
            return redirect(url_for('packages.home'))
        else:
            flash(f'Invalid Email or Old Password', 'danger')
    return render_template('reset_password.html', title='Reset Password', form=form)
