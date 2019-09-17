from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import login_required, current_user
from mailalert.packages.forms import NewPackageForm, PackagePickUpForm
from mailalert.main.forms import StudentSearchForm
from mailalert.packages.utils import send_new_package_email, string_to_bool
from mailalert.models import Package, Student, Hall
from mailalert import db
from datetime import datetime
import json
import re

packages = Blueprint('packages', __name__)


@packages.route("/", methods=['GET', 'POST'])
@packages.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    package_pickup_form = PackagePickUpForm()
    student_search_form = StudentSearchForm()
    setup = request.args.get('setup')
    perishables = Package.query.filter_by(
        perishable=True, status="Active", hall=current_user.hall).all()
    if student_search_form.validate_on_submit():
        return redirect(url_for('packages.student_packages', student_id=student_search_form.student_id.data))
    return render_template('home.html', student_search_form=student_search_form,
                           package_pickup_form=package_pickup_form,
                           setup=setup, perishables=perishables)


@packages.route("/home/<student_id>", methods=['GET', 'POST'])
@login_required
def student_packages(student_id):
    package_pickup_form = PackagePickUpForm()
    student_search_form = StudentSearchForm()

    student = Student.query.filter_by(
        student_id=student_id, hall=current_user.hall).first()
    if not student:
        flash(
            f'That student does not live in {current_user.hall.name}', 'danger')
        return redirect(url_for('packages.home'))

    active_packages = Package.query.filter_by(
        student_id=student.id, status='Active').order_by(Package.delivery_date.desc())
    picked_up_packages = Package.query.filter_by(
        student_id=student.id, status="Picked Up").order_by(Package.delivery_date.desc())

    if student_search_form.submit.data and student_search_form.validate_on_submit():
        return redirect(url_for('packages.student_packages', student_id=student_search_form.student_id.data))

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
        student_id = form.student_id.data
        confirm_student_id = form.student_id_confirm.data
        if confirm_student_id != student_id:
            return jsonify({'error': 'The ID entered does not match this student'})
        package_id_list = request.form.getlist("pick_up")
        for package_id in package_id_list:
            package = Package.query.get(package_id)
            package.status = 'Picked Up'
            package.picked_up_date = datetime.now()
            package.removed = current_user  # record the user that removed the package
        db.session.commit()
        flash('Package was successfully picked up', 'success')
        return jsonify({'success': 'success'})
    return jsonify({'error': form.student_id_confirm.errors})


@packages.route("/newPackage", methods=['GET', 'POST'])
@login_required
def newPackage():
    form = NewPackageForm()
    if form.validate_on_submit():
        student_dict = {}
        name = request.form.getlist('name')
        room_number = request.form.getlist('room_number')
        description = request.form.getlist('description')
        perishable = request.form.getlist('perishable')
        phone_number = request.form.getlist('phone_number')

        # convert perishables from string values to boolean
        perishable = [string_to_bool(x) for x in perishable]

        for i in range(len(name)):
            fname, lname = name[i].split()
            # get the student with the name and room number entered
            student = Student.query.filter_by(
                first_name=fname.capitalize(), last_name=lname.capitalize(), hall=current_user.hall, room_number=room_number[i]).first()
            if not student:
                flash('An error occurred', 'danger')
                return redirect(url_for('packages.newPackage'))

            if phone_number[i]:
                # parse out formatting of phone number
                phone_number = re.sub('[()-]', '', phone_number[i])
                # remove white space
                phone_number = phone_number.replace(' ', '')

                student.phone_number = phone_number

            # create a new package from user input and make the package a child of the student object
            package = Package(
                description=description[i], perishable=perishable[i], inputted=current_user, owner=student, hall=current_user.hall)

            if not package:
                flash('An error occurred', 'danger')
                return redirect(url_for('packages.newPackage'))

            if student.email in student_dict:  # check if the student is already in the dictionary
                num_packages = student_dict[student.email]
                num_packages += 1  # if student is in dict increment their number of packages
                student_dict[student.email] = num_packages
            else:
                student_dict[student.email] = 1
            db.session.add(package)
        db.session.commit()

        ######### uncomment before releasing #########
        # for email, num_packages in student_dict.items():
        # send_new_package_email(email, num_packages)

        flash('Packages sucessfully added!', 'success')
        return redirect(url_for("packages.home"))
    return render_template('newPackage.html', title='New_Package', form=form)


@packages.route("/newPackage/validate", methods=['POST'])
@login_required
def _validate():
    name = request.form.get('name', None)
    room_number = request.form.get('room_number', None)
    phone_number = request.form.get('phone_number', None)
    # check if student phone number needs updating
    update_number = request.form.get('update_number', None)

    if name == None or len(name.split()) <= 1:
        return jsonify({'name_error': 'Enter first and last name of student'})

    fname, lname = name.split()
    fname = fname.capitalize()
    lname = lname.capitalize()

    student = Student.query.filter_by(
        first_name=fname, last_name=lname, hall=current_user.hall).first()

    if not student:
        return jsonify({'name_error': f'This student does not live in {current_user.hall.name} hall'})

    print(student)
    print(room_number)
    if room_number and student.room_number != room_number:
        print('here')
        student = Student.query.filter_by(
            first_name=fname, last_name=lname, room_number=room_number, hall=current_user.hall).first()
        if not student:
            return jsonify({'room_error': 'Student does not live in this room'})

    # make sure phone number is a valid number
    if phone_number and '_' in phone_number:
        return jsonify({'phone_error': 'Invalid phone number'})

    # check if phone number is different than number in database
    if phone_number and student.phone_number:
        # parse out formatting
        phone_number = re.sub('[()-]', '', phone_number)
        # remove white space
        phone_number = phone_number.replace(' ', '')
        if update_number:
            student.phone_number = phone_number
        elif phone_number != student.phone_number:
            return jsonify({'conflicting_numbers': 'True',
                            'current_number': student.phone_number})
    db.session.commit()
    return jsonify({'room_number': student.room_number,
                    'name': fname + ' ' + lname,
                    'phone_number': student.phone_number})
