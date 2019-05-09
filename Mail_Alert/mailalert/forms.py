from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from mailalert.models import Employee


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ManagementForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
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

    def validate_username(self, username):
        employee = Employee.query.filter_by(username=username.data).first()
        if employee:
            raise ValidationError('username is already in use')
