from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify, session
from flask_login import login_user, current_user, logout_user, login_required
from mailalert import db, bcrypt
from mailalert.models import Employee, Hall, Login, Student
from mailalert.employees.forms import ManagementForm, LoginForm, RequestResetForm, ResetPasswordForm, NewPasswordForm, NewHallForm
from mailalert.employees.utils import send_reset_email, send_reset_password_email, generate_random_string
from mailalert.main.utils import requires_access_level
from sqlalchemy import func
from datetime import datetime
import pandas as pd

employees = Blueprint('employees', __name__)


@employees.route("/management", methods=['GET', 'POST'])
@login_required
@requires_access_level('Building Director')
def management():
    form = ManagementForm()
    new_hall_form = NewHallForm()
    # query database for all halls and add them to the list of choices for the halls dropdown
    hall_list = Hall.query.all()
    hall_list = [(hall.id, hall.name) for hall in hall_list]
    form.hall.choices = hall_list
    if form.validate_on_submit():
        existing_employee = Employee.query.filter_by(
            email=form.email.data).first()
        # check if employee already exists. if so update information and make active again
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
    # if the user is not an admin, only get employees that are DR's
    if not current_user.is_admin():
        employees = Employee.query.filter_by(
            access='DR', hall=current_user.hall).all()
    else:
        # user is admin so get all the employees
        employees = Employee.query.all()
    halls = Hall.query.all()
    return render_template('management.html', title='Management', form=form, employees=employees, halls=halls, new_hall_form=new_hall_form)


@employees.route("/management/remove_hall", methods=['POST'])
@login_required
def remove_hall():
    hall_id = request.form.get('hall_id', None)
    hall = Hall.query.get(hall_id)
    if hall:
        student = Student.query.filter_by(hall=hall).first()
        if student:
            return jsonify({'error': f'{hall.name} cannot be removed if an student lives in that hall'})
        employee = Employee.query.filter_by(hall=hall).first()
        if employee:
            return jsonify({'error': f'{hall.name} cannot be removed if an employee works in that hall'})

        db.session.delete(hall)
        db.session.commit()
        return jsonify({'success': 'success'})
    else:
        return jsonify({'error': 'Could not find that hall'})


@employees.route("/management/validate", methods=['POST'])
@login_required
def _validate():
    email = request.form.get('email', None)
    hall = request.form.get('hall', None)
    building_code = request.form.get('building_code', None)
    if email:
        email_exists = Employee.query.filter_by(email=email).first()
        if email_exists and email_exists.active == True:
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
    employee_id_list = request.json
    if employee_id_list:
        for employee_id in employee_id_list:
            employee = Employee.query.filter_by(id=employee_id).first()
            if employee.active == True:
                continue
            employee.active = True
            employee.end_date = None
            employee.reset_password = True
            employee.hired_date = datetime.now()
            password = generate_random_string()
            employee.password = password
            send_reset_password_email(employee, password)
            flash(f'{employee.first_name}\'s account has been reactivated', 'success')
        db.session.commit()
    else:
        flash('No employees were selected', 'danger')
    return jsonify({'success': 'success'})


@employees.route("/management/delete", methods=['POST'])
@login_required
def delete_employee():
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
    if current_user.is_authenticated:
        return redirect(url_for('packages.home'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        # check full email
        employee = Employee.query.filter_by(email=email).first()
        # check if user just entered username
        if not employee:
            employee = Employee.query.filter_by(
                email=email + '@live.kutztown.edu').first()

        if employee and not employee.active:
            flash(
                'Login Unsuccessful. Management has removed you from the list of active employees', 'danger')
            return render_template('login.html', title='Login', form=form)
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
    # get the last login date by the current user and log logout date and time
    current_user.logins[-1].logout_date = datetime.now()
    db.session.commit()
    logout_user()
    return redirect(url_for('employees.login'))


@employees.route("/forgot_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('packages.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(email=form.email.data).first()
        ######### uncomment before releasing #########
        send_reset_email(employee)
        flash(
            f'An email has been sent to {employee.email} with instructions to reset your password.', 'info')
        return redirect(url_for('employees.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@employees.route("/forgot_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('packages.home'))
    employee = Employee.verify_reset_token(token)
    if employee is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('employees.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        employee.password = form.password.data
        employee.reset_password = False
        db.session.commit()
        flash('Your password has been reset!', 'success')
        return redirect(url_for('employees.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@employees.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    form = NewPasswordForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(email=form.email.data).first()
        # if the current users password matches the old password field
        if employee and bcrypt.check_password_hash(employee.password, form.old_password.data):
            employee.password = form.new_password.data
            employee.reset_password = False
            db.session.commit()
            flash('Your password has been changed!', 'success')
            return redirect(url_for('employees.login'))
        else:
            flash(f'Invalid email or password', 'danger')
    return render_template('reset_password.html', title='Reset Password', form=form)
