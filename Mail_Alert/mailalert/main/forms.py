from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, RadioField, IntegerField
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
    userID = IntegerField('Student Identification', validators=[
        DataRequired(message="Please enter a student ID")])
    submit = SubmitField("Search")

    def validate_userID(self, field):
        student = Student.query.filter_by(userID=field.data).first()
        if not student:
            raise ValidationError('We could not find that student')
