from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FieldList, BooleanField, HiddenField
from wtforms.validators import DataRequired, Length, Email, ValidationError, NumberRange
from mailalert.models import Student


class NewPackageForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    roomNumber = StringField('Rooom Number', validators=[DataRequired()])
    status = StringField('Package Status', default='Active')
    description = StringField('Description', validators=[DataRequired()])
    perishable = BooleanField('Perishable')
    submit = SubmitField('Submit')


class PackagePickUpForm(FlaskForm):
    pick_up = BooleanField('Pick up Package')
    student_id = HiddenField('Student ID')
    ID_confirm = IntegerField('ID Confirm', validators=[
                              DataRequired(message='Please enter a student ID')])
    confirm = SubmitField('Confirm')

    def validate_ID_confirm(self, field):
        student = Student.query.filter_by(userID=field.data).first()
        if not student:
            raise ValidationError('That student does not exist')
