from flask import Flask, render_template, url_for, flash, redirect, request, abort
from mailalert import app, db, bcrypt
from mailalert.models import Employee 
from mailalert.forms import LoginForm, ManagementForm
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
@login_required
def home():
    return render_template('home.html')

@app.route("/newPackage")
@login_required
def newPackage():
    return render_template('newPackage.html', title='New_Package')


@app.route("/management", methods=['GET', 'POST'])
# @login_required
def management():
    form = ManagementForm()
    employees = Employee.query.all()
    if form.validate_on_submit():  # this will only be true if there is a form.submit in management.html
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # generate a password hash for the user that is being created
        dr = Employee(username=form.username.data, fname=form.firstName.data, lname=form.lastName.data, workinghall=form.hall.data, password=hashed_password) 
        db.session.add(dr)  # creates a new employee object (can be found in models.py) so that we can insert it into our database
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('management'))
    return render_template('management.html', title='Management', form=form, employees=employees)


@app.route("/management/delete", methods=['POST'])
# @login_required
def delete_employee():
    employee_id_list = request.form.getlist("del_employees")
    if employee_id_list:  # make sure the user selected at least one employee
        for employee_id in employee_id_list:
            employee = Employee.query.get(employee_id)   # get the employee object using its id
            flash(f'{employee.username} was successfully deleted!', 'success')
            db.session.delete(employee)
        db.session.commit()
    else:
        flash('No employees were selected!', 'danger')
    return redirect(url_for('management'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(username=form.username.data).first()  
        if employee and bcrypt.check_password_hash(employee.password, form.password.data):
            login_user(employee)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Check Username and Password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))
