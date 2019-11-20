from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from mailalert.models import Employee


class LoginForm(FlaskForm):
    email = StringField('Email ', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class NewHallForm(FlaskForm):
    hall = StringField('Hall', validators=[DataRequired()])
    building_code = StringField('Building Code', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ManagementForm(FlaskForm):
    email = StringField('Email ', validators=[DataRequired(), Email()])
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    role = SelectField('Role', choices=[
                       ('Admin', 'Admin'), ('Building Director', 'Building Director'), ('DR', 'DR')])
    hall = SelectField('Working Hall', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')


class RequestResetForm(FlaskForm):
    email = StringField('Email ', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        employee = Employee.query.filter_by(email=email.data).first()
        if employee is None:
            raise ValidationError(
                'There is no account associated with that email. Contact your supervisor about account access.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class NewPasswordForm(FlaskForm):
    email = StringField('Email ', validators=[DataRequired(), Email()])
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
                                         DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Reset Password')
