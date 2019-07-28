from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from mailalert import db, bcrypt
from mailalert.models import Employee
from mailalert.employees.forms import ManagementForm, LoginForm, RequestResetForm, ResetPasswordForm, EditEmployeeForm, NewPasswordForm
from mailalert.employees.utils import send_reset_email, generate_random_string, send_temp_password_email
from mailalert.main.utils import requires_access_level

employees = Blueprint('employees', __name__)

@employees.route("/management", methods=['GET', 'POST'])
@login_required
@requires_access_level('Building Director')
def management():
    form = ManagementForm()
    if form.validate_on_submit():  # this will only be true if ManagementForm fields are all correct
        password = generate_random_string()
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')  # generate a password hash for the user that is being created
        employee = Employee(email=form.email.data, fname=form.firstName.data, 
                            lname=form.lastName.data, access=form.role.data,    
                            workinghall=form.hall.data, password=hashed_password) 
        db.session.add(employee)  # creates a new employee object (can be found in models.py) so that we can insert it into our database
        db.session.commit()
        send_temp_password_email(employee, password)
        flash(f'Account created for {employee.email}!', 'success')
    employees = Employee.query.all()
    return render_template('management.html', title='Management', form=form, employees=employees)


@employees.route("/management/delete", methods=['POST'])
# @login_required
def delete_employee():
    employee_id_list = request.form.getlist("del_employees")
    if employee_id_list:  # make sure the user selected at least one employee
        for employee_id in employee_id_list:
            employee = Employee.query.get(employee_id)   # get the employee object using its id
            flash(f'{employee.fname} was successfully deleted!', 'success')
            db.session.delete(employee)
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
        return redirect(url_for('packages.home'))
    form = LoginForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(email=form.email.data).first()  
        if employee and bcrypt.check_password_hash(employee.password, form.password.data):
            login_user(employee)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('packages.home'))
        else:
            flash('Login Unsuccessful. Check email and Password', 'danger')
    return render_template('login.html', title='Login', form=form)

@employees.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('employees.login'))


@employees.route("/forgot_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('packages.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(email=form.email.data).first()
        send_reset_email(employee)
        flash(f'An email has been sent to {employee.email} with instructions to reset your password.', 'info')
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
    if form.validate_on_submit():  # this will only be true if there is a form.submit in management.html
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # generate a password hash for the user that is being created
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
            hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            employee.password = hashed_password
            db.session.commit()
            flash('Your password has been changed!', 'success')
            return redirect(url_for('employees.login'))
        else:
            flash(f'Invalid email or password', 'danger')
    return render_template('reset_password.html', title='New Password', form=form)