from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, TextAreaField, RadioField, IntegerField, FileField, SelectField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from mailalert.models import Message, Student


class ComposeEmailForm(FlaskForm):
    recipient_email = StringField(
        'Email', validators=[DataRequired(), Email()])
    cc_recipient = StringField('Email')
    compose_submit = SubmitField('Send')


class CreateMessageForm(FlaskForm):
    new_message = TextAreaField('New Message', validators=[Length(
        min=10, message='This message is not long enough')])
    create_submit = SubmitField('Create')


class StudentSearchForm(FlaskForm):
    # student_id = IntegerField('Student Identification', validators=[
    student_id = StringField('Student Identification')
    submit = SubmitField("Search")
