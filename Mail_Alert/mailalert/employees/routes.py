from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from mailalert import db, bcrypt
from mailalert.models import Employee, Hall, Login
from mailalert.employees.forms import ManagementForm, LoginForm, RequestResetForm, ResetPasswordForm, NewPasswordForm
from mailalert.employees.utils import send_reset_email, generate_random_string, send_temp_password_email
from mailalert.main.utils import requires_access_level
from datetime import datetime

employees = Blueprint('employees', __name__)


@employees.route("/management", methods=['GET', 'POST'])
@login_required
@requires_access_level('Building Director')
def management():
    form = ManagementForm()
    # query database for all halls and add them to the list of choices for the halls dropdown
    hall_list = Hall.query.all()
    hall_list = [(hall.id, hall.name) for hall in hall_list]
    form.hall.choices = hall_list
    if form.validate_on_submit():
        existing_employee = Employee.query.filter_by(
            email=form.email.data).first()
        # check if employee already exists. if so update information and make active again
        if existing_employee:
            existing_employee.hall = Hall.query.get(form.hall.data)
            existing_employee.first_name = form.firstName.data.capitalize()
            existing_employee.last_name = form.lastName.data.capitalize()
            existing_employee.access = form.role.data
            existing_employee.active = True
            flash(
                f'{existing_employee.first_name}\'s account has been reactivated!', 'success')
        else:
            password = generate_random_string()
            hashed_password = bcrypt.generate_password_hash(password).decode(
                'utf-8')  # generate a password hash for the user that is being created
            hall = Hall.query.get(form.hall.data)  # get hall object
            employee = Employee(email=form.email.data, first_name=form.firstName.data.capitalize(),
                                last_name=form.lastName.data.capitalize(), access=form.role.data,
                                hall=hall, password=hashed_password)
            flash(f'Account created for {employee.email}!', 'success')
            send_temp_password_email(employee, password)
            db.session.add(employee)
        db.session.commit()
    employees = Employee.query.filter(Employee.active == True).all()
    return render_template('management.html', title='Management', form=form, employees=employees)


@employees.route("/management/validate", methods=['POST'])
@login_required
def _validate():
    email = request.form['email']
    email_exists = Employee.query.filter_by(email=email).first()
    if email_exists and email_exists.active == True:
        return jsonify({'error': 'This email is already in use'})
    return jsonify({'success': 'success'})


@employees.route("/management/delete", methods=['POST'])
@login_required
def delete_employee():
    employee_id_list = request.form.getlist("del_employees")
    if employee_id_list:  # make sure the user selected at least one employee
        for employee_id in employee_id_list:
            # get the employee object using its id
            employee = Employee.query.get(employee_id)
            employee.end_date = datetime.now()  # record employees end date
            employee.active = False
            flash(f'{employee.first_name} was successfully deactivated!', 'success')
        db.session.commit()
    else:
        flash('No employees were selected!', 'danger')
    return redirect(url_for('employees.management'))


# @employees.route("/management/edit", methods=['POST'])
# @login_required
# def edit_employee():
#     form = EditEmployeeForm()
#     if form.validate_on_submit():
#         employee = Employee.query.filter_by(email=form.email.data).first()
#         employee.email = form.email.data
#         employee.fname = form.firstName.data
#         employee.lname = form.lastName.data
#         employee.workinghall = form.hall.data
#         db.session.commit()
#     return redirect(url_for('employees.management'))


@employees.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(email=form.email.data).first()
        if not employee.active:
            flash(
                'Login Unsuccessful. Management has removed you from the list of active employees', 'danger')
            return render_template('login.html', title='Login', form=form)
        if employee and bcrypt.check_password_hash(employee.password, form.password.data):
            login_user(employee)
            logins = Login.query.first()
            # check if there has ever been a login
            first_login = False if logins else True
            # log when user logs in
            login = Login(login_date=datetime.now(), employee=current_user)
            db.session.add(login)
            db.session.commit()
            if first_login is True:
                return redirect(url_for('main.home', setup=first_login))
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
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
        return redirect(url_for('main.home'))
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
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    employee = Employee.verify_reset_token(token)
    if employee is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('employees.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():  # this will only be true if there is a form.submit in management.html
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            'utf-8')  # generate a password hash for the user that is being created
        employee.password = hashed_password
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
            hashed_password = bcrypt.generate_password_hash(
                form.new_password.data).decode('utf-8')
            employee.password = hashed_password
            db.session.commit()
            flash('Your password has been changed!', 'success')
            return redirect(url_for('employees.login'))
        else:
            flash(f'Invalid email or password', 'danger')
    return render_template('reset_password.html', title='New Password', form=form)
