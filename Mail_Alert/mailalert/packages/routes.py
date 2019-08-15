from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import login_required, current_user
from mailalert.packages.forms import NewPackageForm, PackagePickUpForm
from mailalert.main.forms import StudentSearchForm
from mailalert.packages.utils import string_to_bool
from mailalert.models import Package, Student
from mailalert import db
from datetime import datetime
import json

packages = Blueprint('packages', __name__)


@packages.route("/home/<int:student_id>", methods=['GET', 'POST'])
@login_required
def student_packages(student_id):
    package_pickup_form = PackagePickUpForm()
    student_search_form = StudentSearchForm()

    student = Student.query.filter_by(userID=student_id).first_or_404()

    active_packages = Package.query.filter_by(
        student_id=student.id, status='Active').order_by(Package.delivery_date.desc())
    picked_up_packages = Package.query.filter_by(
        student_id=student.id, status="Picked Up").order_by(Package.delivery_date.desc())

    if student_search_form.submit.data and student_search_form.validate_on_submit():
        return redirect(url_for('packages.student_packages', student_id=student_search_form.userID.data))

    return render_template('student_packages.html', student=student,
                           package_pickup_form=package_pickup_form,
                           student_search_form=student_search_form,
                           active_packages=active_packages,
                           picked_up_packages=picked_up_packages)


@packages.route("/home/pickup_package", methods=['POST'])
@login_required
def _pickup_package():
    form = PackagePickUpForm()
    if form.validate_on_submit():
        student_id = int(form.student_id.data)
        confirm_student_id = form.ID_confirm.data
        if confirm_student_id != student_id:
            return jsonify({'error': 'The ID entered does not match this student'})
        package_id_list = request.form.getlist("pick_up")
        for package_id in package_id_list:
            package = Package.query.get(package_id)
            package.status = 'Picked Up'
            package.picked_up_date = datetime.now()
        db.session.commit()
        flash('Package was successfully picked up', 'success')
        return jsonify({'success': 'success'})
    return jsonify({'error': form.ID_confirm.errors})


@packages.route("/newPackage", methods=['GET', 'POST'])
@login_required
def newPackage():
    form = NewPackageForm()
    if form.validate_on_submit():
        name = request.form.getlist('name')
        roomNumber = request.form.getlist('roomNumber')
        description = request.form.getlist('description')
        perishable = request.form.getlist('perishable')

        for i in range(len(name)):
            fname, lname = name[i].split()
            fname = fname.capitalize()
            lname = lname.capitalize()
            # convert perishable from string value to boolean
            result = string_to_bool(perishable[i])
            # get the student with the name and room number entered
            student = Student.query.filter_by(
                fname=fname, lname=lname, room=roomNumber[i]).first()
            # create a new package from user input and make the package a child of the student object
            package = Package(
                description=description[i], perishable=result, dr=current_user.fname, owner=student)
            db.session.add(package)
        db.session.commit()

        flash('Packages sucessfully added!', 'success')
        return redirect(url_for("main.home"))
    return render_template('newPackage.html', title='New_Package', form=form)


@packages.route("/newPackage/validate", methods=['POST'])
@login_required
def _validate():
    name = request.form['name']
    roomNumber = request.form['roomNumber']

    if len(name.split()) <= 1:
        return jsonify({'name_error': 'Enter first and last name of student'})

    fname, lname = name.split()
    fname = fname.capitalize()
    lname = lname.capitalize()

    student = Student.query.filter_by(fname=fname, lname=lname).first()
    if not student:
        return jsonify({'name_error': 'Student does not exist'})

    if roomNumber:
        if student.room != roomNumber:
            return jsonify({'room_error': 'Student does not live in this room',
                            'roomNumber': student.room,
                            'name': fname + ' ' + lname})

    return jsonify({'roomNumber': student.room,
                    'name': fname + ' ' + lname})


@packages.route("/packages", methods=['GET'])
@login_required
def package():
    page = request.args.get('page', 1, type=int)
    packages = Package.query.filter_by(perishable=False).order_by(
        Package.delivery_date.desc()).paginate(page=page, per_page=10)
    return render_template('packages.html', title="Packages", packages=packages)
