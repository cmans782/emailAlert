from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FieldList
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from mailalert.models import Employee


class NewPackageForm(FlaskForm):
    firstName = StringField('First Name',validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    roomNumber = StringField('Rooom Number', validators=[DataRequired()])
    status = StringField('Package Status', default='Active')
    description = StringField('Description')
    submit = SubmitField('Submit')