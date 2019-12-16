from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, RadioField, IntegerField
from wtforms.validators import DataRequired, Email, Length
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


class NewIssueForm(FlaskForm):
    summary = StringField('Summary', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    issueType = RadioField('Type of Feedback',
                           validators=[DataRequired()],
                           choices=[('Bug', 'Bug'),
                                    ('New Feature', 'New Feature Request')])
    priority = RadioField('Priority of Feedback',
                          validators=[DataRequired()],
                          choices=[('Trivial', 'Trivial - spelling error, etc.'),
                                   ('Low', 'Low - Site works, visual problem'),
                                   ('Medium', 'Medium - Site behaving poorly or slowly'),
                                   ('High', 'High - Site functionality limited'),
                                   ('Critical', 'Critical - Site broken or functionality broken'),
                                   ('New Feature', 'New Feature Request')])
    submit = SubmitField('Submit')
