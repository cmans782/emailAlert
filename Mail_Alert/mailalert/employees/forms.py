from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, ValidationError
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
    email = StringField('Email ', validators=[DataRequired()])
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
        """
        validate that the email entered is associated with an account

        Parameters:
            self - current user object
            email - the users email to be validated

        Returns: 
            None
        """
        employee = Employee.query.filter_by(email=email.data).first()
        if employee is None:
            raise ValidationError(
                'There is no account associated with that email')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField(
        'Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')


class NewPasswordForm(FlaskForm):
    email = StringField('Email ', validators=[DataRequired()])
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField(
        'Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')
