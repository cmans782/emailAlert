from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FieldList, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


class NewPackageForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    roomNumber = StringField('Rooom Number', validators=[DataRequired()])
    status = StringField('Package Status', default='Active')
    description = StringField('Description', validators=[DataRequired()])
    perishable = BooleanField('Perishable')
    submit = SubmitField('Submit')

class StudentInfoForm (FlaskForm):
    userID = StringField('Student Identification', validators=[DataRequired()])
    pick_up = BooleanField('Pick up Package')
    submit = SubmitField("Search")
