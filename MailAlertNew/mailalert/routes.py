from flask import Flask, render_template, url_for, flash, redirect
from mailalert import app, db, bcrypt
from mailalert.models import DR 
from mailalert.forms import LoginForm, addEmployee
from flask_login import login_user, current_user, logout_user


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/newPackage")
def newPackage():
    return render_template('newPackage.html', title='New_Package')


@app.route("/addemployee", methods=['GET', 'POST'])
def addemployee():
    form = addEmployee()
    employees = DR.query.all()
    if form.validate_on_submit():
        dr = DR(username=form.username.data, fname=form.firstName.data, lname=form.lastName.data, workinghall='BH') 
        db.session.add(dr)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('addemployee'))
    return render_template('addemployee.html', title='Add Employee', form=form, employees=employees)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()  
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
