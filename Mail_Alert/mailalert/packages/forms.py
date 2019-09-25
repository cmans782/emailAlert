from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FieldList, BooleanField, HiddenField, SelectField
from wtforms.validators import DataRequired, Length, Email, ValidationError, NumberRange
from mailalert.models import Student


class NewPackageForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number')
    room_number = StringField('Rooom Number', validators=[DataRequired()])
    status = StringField('Package Status', default='Active')
    description = StringField('Description', validators=[DataRequired()])
    perishable = BooleanField('Perishable')
    submit = SubmitField('Submit')


class PackagePickUpForm(FlaskForm):
    pick_up = BooleanField('Pick up Package')
    student_id_confirm = StringField('ID Confirm', validators=[
        DataRequired(message='Please enter a student ID')])
    confirm = SubmitField('Confirm')

    def validate_student_id_confirm(self, field):
        student = Student.query.filter_by(student_id=field.data).first()
        if not student:
            raise ValidationError('Student does not exist')
