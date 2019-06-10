from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from mailalert.models import Employee


class LoginForm(FlaskForm):
    email = StringField('Email ', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ManagementForm(FlaskForm):
    email = StringField('Email ', validators=[DataRequired(), Email()])
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    phone = StringField('Phone Number')
    hall = SelectField('Working Hall', choices=[('Dixon North', 'Dixon North'), ('Dixon South', 'Dixon South'), ('Village South', 'Village South'),
                                                ('University Place', 'University Place'), ('Bonner', 'Bonner'), ('Johnson', 'Johnson'),
                                                ('Schuylkill', 'Schuylkill'), ('Lehigh', 'Lehigh'), ('Beck', 'Beck'), 
                                                ('Berks', 'Berks'), ('Deatrick', 'Deatrick'), ('Rothermel', 'Rothermel'), ('Honors', 'Honors')])   
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_email(self, email):
        employee = Employee.query.filter_by(email=email.data).first()
        if employee:
            raise ValidationError('email is already in use')

class RequestResetForm(FlaskForm):
    email = StringField('Email ', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        employee = Employee.query.filter_by(email=email.data).first()
        if employee is None:
            raise ValidationError('There is no account with that email. Contact your supervisor about account access.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')