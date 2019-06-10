from flask import render_template, Blueprint
from flask_login import login_required

packages = Blueprint('packages', __name__)

@packages.route("/newPackage")
@login_required
def newPackage():
    return render_template('newPackage.html', title='New_Package')

@packages.route("/packages")
@login_required
def package():
    return render_template('packages.html', title="Packages")