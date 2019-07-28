from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import login_required, current_user
from mailalert.packages.forms import NewPackageForm, StudentInfoForm 
from mailalert.packages.utils import string_to_bool
from mailalert.models import Package, Student
from mailalert import db
from datetime import datetime
import json

packages = Blueprint('packages', __name__)

@packages.route("/", methods=['GET', 'POST'])
@packages.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    packages, student = [], []
    form = StudentInfoForm()
    if form.validate_on_submit():
        student_name = form.userID.data
        fname, lname = student_name.split()
        student = Student.query.filter_by(fname=fname, lname=lname).first()
        page = request.args.get('page', 1, type=int)
        packages = Package.query.filter_by(student_id=student.id).order_by(Package.delivery_date.desc()).paginate(page=page, per_page=7)

    return render_template('home.html', packages=packages, student=student, form=form)


@packages.route("/pickup_package", methods=['POST'])
@login_required
def _pickup_package():
    
    package_id_list = request.form.getlist("pick_up")
    if package_id_list:  # make sure the user selected at least one package
        for package_id in package_id_list:
            package = Package.query.get(package_id)   # get the package object using its id
            package.status = 'Picked Up'
            package.picked_up_date = datetime.now()
            flash('Packages were successfully picked up!', 'success')
        db.session.commit()
    else:
        flash('No packages were selected!', 'danger')
    return redirect(url_for('packages.home'))


@packages.route("/newPackage", methods=['GET', 'POST'])
@login_required
def newPackage():
    form = NewPackageForm()
    if form.validate_on_submit():
        firstName = request.form.getlist('firstName')
        lastName = request.form.getlist('lastName')
        roomNumber = request.form.getlist('roomNumber')
        description = request.form.getlist('description')
        perishable = request.form.getlist('perishable')

        for i in range(len(firstName)):
            result = string_to_bool(perishable[i])  # convert perishable from string value to boolean
            # get the student with the name and room number entered
            student = Student.query.filter_by(fname=firstName[i], lname=lastName[i], room=roomNumber[i]).first()
            # create a new package from user input and make the package a child of the student object
            package = Package(description=description[i], perishable=result, dr=current_user.fname, owner=student)                                                         
            db.session.add(package)
        db.session.commit()

        flash('Packages sucessfully added!', 'success')
        return redirect(url_for("packages.home"))
    return render_template('newPackage.html', title='New_Package', form=form)

@packages.route("/packages", methods=['GET'])
@login_required
def package():
    page = request.args.get('page', 1, type=int)
    packages = Package.query.filter_by(perishable=False).order_by(Package.delivery_date.desc()).paginate(page=page, per_page=10)
    return render_template('packages.html', title="Packages", packages=packages)
