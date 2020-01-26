from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import login_required, current_user
from mailalert.packages.forms import NewPackageForm, PackagePickUpForm, ResubscribeForm
from mailalert.main.forms import StudentSearchForm
from mailalert.packages.utils import send_new_package_email, string_to_bool, parse_name, get_package_num
from mailalert.models import Package, Student, Phone, SentMail
from mailalert.config import Config
from mailalert import db
from datetime import datetime
import json
import re


packages = Blueprint('packages', __name__)


@packages.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    """
    render home.html and display perishables table if there are any.
    Allow for perishables to be picked up from here

    Returns:
        GET -
            renders home.html
        POST -
            redirect to student_packages route
    """
    package_pickup_form = PackagePickUpForm()
    student_search_form = StudentSearchForm()
    perishables = Package.query.filter_by(
        perishable=True, status="Active", hall=current_user.hall).all()
    if student_search_form.validate_on_submit():
        return redirect(url_for('packages.student_packages', student_id=student_search_form.student_id.data))
    return render_template('home.html', student_search_form=student_search_form,
                           package_pickup_form=package_pickup_form, perishables=perishables)


@packages.route("/home/search_student", methods=['POST'])
@login_required
def _search_student():
    """
    validate that the student ID entered is valid

    Returns:
        Json "success" if the ID is valid, otherwise "error"
    """
    student_id = request.form.get('student_id', None)
    if not student_id:
        return jsonify({'success': 'success'})
    student = Student.query.filter_by(
        student_id=student_id, hall=current_user.hall, active=True).first()
    if not student:
        return jsonify({'error': f'This student does not live in {current_user.hall.name} hall'})

    return jsonify({'success': 'success'})


@packages.route("/home/<student_id>", methods=['GET', 'POST'])
@login_required
def student_packages(student_id):
    """
    Display all of a students active and picked up packages.
    Allow employee to search for a different student

    Returns:
        GET - render student_packages.html
        POST -
            success - redirect for student_packages with new student
            error - redirect for home route
    """
    package_pickup_form = PackagePickUpForm()
    student_search_form = StudentSearchForm()

    student = Student.query.filter_by(
        student_id=student_id, hall=current_user.hall, active=True).first()
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
    """
    Mark a package as picked up

    Returns:
        "success" json response if package was successfully
        picked up, otherwise "error"
    """
    form = PackagePickUpForm()
    if form.validate_on_submit():
        confirm_student_id = form.student_id_confirm.data
        package_id_list = request.form.getlist("pick_up")
        for package_id in package_id_list:
            package = Package.query.get(package_id)
            if package.owner.student_id != confirm_student_id:
                return jsonify({'error': 'The ID entered does not match this student'})
            package.status = 'Picked Up'
            package.picked_up_date = datetime.utcnow()
            package.removed = current_user  # record the user that removed the package
        db.session.commit()
        flash('Package was successfully picked up', 'success')
        return jsonify({'success': 'success'})
    return jsonify({'error': form.student_id_confirm.errors})


@packages.route("/newPackage", methods=['GET', 'POST'])
@login_required
def newPackage():
    """
    add new packages for students and send them an
    email notification

    Returns:
        GET - render newPackage.html
        POST -
            success - redirect for home route
            error - redirect for newPackage route
    """
    form = NewPackageForm()
    if form.validate_on_submit():
        student_dict = {}
        name_list = request.form.getlist('name')
        room_number = request.form.getlist('room_number')
        description = request.form.getlist('description')
        perishable = request.form.getlist('perishable')
        phone_number_list = request.form.getlist('phone_number')
        phone_number_obj = None
        # convert perishables from string values to boolean
        perishable = [string_to_bool(x) for x in perishable]

        for i in range(len(name_list)):
            name = ''.join(name_list[i])
            fname, lname = parse_name(name)
            # get the student with the name and room number entered
            student = Student.query.filter_by(first_name=fname.title(), last_name=lname.title(),
                                              hall=current_user.hall, room_number=room_number[i]).first()
            if not student:
                flash('Error getting student', 'danger')
                return redirect(url_for('packages.newPackage'))

            if perishable[i]:
                phone_number_obj = None
                # parse out formatting of phone number
                phone_number = re.sub('[()-]', '', phone_number_list[i])
                # remove white space
                phone_number = phone_number.replace(' ', '')
                # if student does not have any phone numbers saved in db
                if student.phone_numbers == []:
                    # create new phone number
                    phone_number_obj = Phone(phone_number=phone_number)
                    # assign number obj to student
                    student.phone_numbers.append(phone_number_obj)
                # if the student already has a number saved in db
                if not phone_number_obj:
                    phone_number_obj = Phone.query.filter_by(
                        phone_number=phone_number).first()
                    if phone_number_obj == None:
                        flash('Error getting phone number', 'danger')
                        return redirect(url_for('packages.newPackage'))

            package_num = get_package_num(student)
            package = Package(package_number=package_num, description=description[i],
                              perishable=perishable[i], inputted=current_user, owner=student,
                              hall=current_user.hall, phone=phone_number_obj)

            if not package:
                flash('Error getting package', 'danger')
                return redirect(url_for('packages.newPackage'))

            # only add students to the dictonary that are subscribed to email notifications
            if student.subscribed:
                if student.email in student_dict:  # check if the student is already in the dictionary
                    num_packages = student_dict[student.email]
                    num_packages += 1  # if student is in dict increment their number of packages
                    student_dict[student.email] = num_packages
                else:
                    student_dict[student.email] = 1
            db.session.add(package)

        for email, num_packages in student_dict.items():
            student = Student.query.filter_by(email=email).first()
            send_new_package_email(student, num_packages)
            sent_mail = SentMail(employee=current_user, student=student)
            db.session.add(sent_mail)
        db.session.commit()

        flash('Packages sucessfully added!', 'success')
        return redirect(url_for("packages.home"))
    return render_template('newPackage.html', title='New_Package', form=form)


@packages.route("/newPackage/validate", methods=['POST'])
@login_required
def _validate():
    """
    Validate the package information as it is being entered

    Returns: 
        POST - 
            success - student name, room and phone number as a JSON response 
            error - JSON response reporting what the error is 
    """
    name = request.form.get('name', None)
    room_number = request.form.get('room_number', None)
    phone_number = request.form.get('phone_number', None)
    # check if student has a new phone number
    new_number = request.form.get('new_number', None)

    if name == None or len(name.split()) <= 1:
        return jsonify({'success': 'success'})

    fname, lname = parse_name(name)

    student = Student.query.filter_by(
        first_name=fname, last_name=lname, hall=current_user.hall, active=True).first()

    if not student:
        return jsonify({'name_error': f'This student does not live in {current_user.hall.name} hall'})

    if room_number and student.room_number != room_number:
        student = Student.query.filter_by(
            first_name=fname, last_name=lname, room_number=room_number, hall=current_user.hall).first()
        if not student:
            return jsonify({'room_error': 'Student does not live in this room'})

    # make sure phone number is a valid number
    if phone_number and '_' in phone_number:
        return jsonify({'phone_error': 'Invalid phone number'})

    # if student has phone numbers in db get the most recent one, else None
    recent_phone_number = student.phone_numbers[-1].phone_number if student.phone_numbers else None

    # check if there was a phone number submitted and see if there is
    # a number saved in the db for this student
    if phone_number:
        # parse out formatting
        phone_number = re.sub('[()-]', '', phone_number)
        # remove white space
        phone_number = phone_number.replace(' ', '')
        # check if user confirmed new number. if so, add it to db for this student
        if new_number:
            # create new phone number
            phone_number_obj = Phone(phone_number=phone_number)
            # assign number obj to student
            student.phone_numbers.append(phone_number_obj)
        # if student does not have any phone numbers in db
        elif recent_phone_number == None:
            return jsonify({'new_number': 'True',
                            'current_number': recent_phone_number})
        # if the phone number entered by user does not match most recent phone number
        # or if there is no number saved for the student
        elif phone_number != recent_phone_number:
            # get all the phone numbers in db for this student
            student_numbers = [
                obj.phone_number for obj in student.phone_numbers]
            if phone_number not in student_numbers:
                return jsonify({'new_number': 'True',
                                'current_number': recent_phone_number})
            else:
                # if the number is in db then reassign recent_phone_number
                recent_phone_number = phone_number
    db.session.commit()
    return jsonify({'room_number': student.room_number,
                    'name': fname + ' ' + lname,
                    'phone_number': recent_phone_number})


@packages.route("/newPackage/suggestions", methods=['GET', 'POST'])
@login_required
def suggestions():
    """
    create a list of name suggestions based on what the user
    is inputting. Works for search box and when entering 
    student first name, last name, and room number

    Returns: 
        JSON response with all of the student suggestions

    """
    suggestions = []
    # name and room_number are for when entering a new package
    name = request.args.get('name', None)
    room_number = request.args.get('room_number', None)
    # search bar is for when entering a name in the search bar
    search_bar = request.args.get('search_bar', None)
    # the process of search bar and name are the same. assign
    # name the value of search_bar if name has no value
    if search_bar and name == None:
        name = search_bar

    if name:
        name = name.title()
        # if the user only typed in a first or a last name
        if len(name.split()) == 1:
            # get all the students that contain name in their first or last name
            # and are in the same hall as the user
            students = Student.query.filter((Student.first_name.contains(name)) |
                                            (Student.last_name.contains(name)),
                                            Student.hall == current_user.hall,
                                            Student.active == True).all()
        elif len(name.split()) > 1:
            first_name, last_name = parse_name(name)

            students = Student.query.filter(
                Student.first_name.contains(first_name,) |
                Student.last_name.contains(last_name),
                Student.hall == current_user.hall,
                Student.active == True).all()

    if search_bar:
        # if no name was found for what was entered, look based on id
        if not students:
            students = Student.query.filter(
                Student.student_id.contains(search_bar)).all()

        for student in students:
            data = {'value': student.student_id,
                    'label': student.first_name + ' ' + student.last_name + ' ' + student.student_id}
            suggestions.append(data)

    elif name:
        for student in students:
            data = {'value': student.first_name + ' ' + student.last_name,
                    'label': student.first_name + ' ' + student.last_name + ' ' + student.room_number}
            suggestions.append(data)

    elif room_number:
        if len(room_number.split()) == 1:
            students = Student.query.filter(
                Student.room_number.contains(room_number),
                Student.hall == current_user.hall).all()

        for student in students:
            data = {'value': student.room_number,
                    'label': student.first_name + ' ' + student.last_name + ' ' + student.room_number}
            suggestions.append(data)
    return jsonify(suggestions[:8])


@packages.route("/subscription/<student_email>", methods=['GET', 'POST'])
def subscription(student_email):
    """
    Manage the students email subscription 
    GET request will unsubscribe user
    POST request will resubscribe user 

    Returns: 
        GET - render unsubscribed.html
        POST - render resubscibed.html

    """
    form = ResubscribeForm()
    student = Student.query.filter_by(email=student_email).first()
    # if form is sumbitted resubscribe student to emails
    if form.is_submitted():
        student.subscribed = True
        db.session.commit()
        return render_template('resubscribed.html', title='Resubscribed')
    # unsubscribe the student from emails
    student.subscribed = False
    db.session.commit()
    return render_template('unsubscribed.html', title='Unsubscribed', form=form)
