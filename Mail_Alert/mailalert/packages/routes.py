from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import login_required, current_user
from mailalert.packages.forms import NewPackageForm 
from mailalert.models import Package
from mailalert import db
import json

packages = Blueprint('packages', __name__)


@packages.route("/newPackage", methods=['GET', 'POST'])
# @login_required
def newPackage():
    form = NewPackageForm()
    if form.validate_on_submit():
        firstName = request.form.getlist('firstName')
        lastName = request.form.getlist('lastName')
        roomNumber = request.form.getlist('roomNumber')
        description = request.form.getlist('description')
        perishable = request.form.getlist('perishable')
        for i in range(len(firstName)):
            print(request.form.listvalues())   
        
        for i in range(len(firstName)):
            package = Package(fname=firstName[i], lname=lastName[i], roomNum=roomNumber[i], description=description[i], perishable=True, dr=current_user.fname)                                                         
            db.session.add(package)
        db.session.commit()

        flash('Packages sucessfully added!', 'success')
        return redirect(url_for("main.home"))
    return render_template('newPackage.html', title='New_Package', form=form)

@packages.route("/packages", methods=['GET'])
# @login_required
def package():
    page = request.args.get('page', 1, type=int)
    packages = Package.query.order_by(Package.delivery_date.desc()).paginate(page=page, per_page=10)
    return render_template('packages.html', title="Packages", packages=packages)


# @packages.route("/packages/<str:fname>", methods=['GET', 'POST'])
# @login_required
# def package():
#     page = request.args.get('page', 1, type=int)
#     packages = Package.query.order_by(Package.delivery_date.desc()).paginate(page=page, per_page=10)
#     return render_template('packages.html', title="Packages", packages=packages)