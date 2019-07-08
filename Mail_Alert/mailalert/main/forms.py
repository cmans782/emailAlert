from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Email, Length
from mailalert.models import Message


class ComposeEmailForm(FlaskForm):
    recipient_email = StringField('Email', validators=[DataRequired(), Email()])
    cc_recipient = StringField('Email')
    compose_submit = SubmitField('Send')


class CreateMessageForm(FlaskForm):
    new_message = TextAreaField('New Message', validators=[Length(min=10, message='This message is not long enough')])
    create_submit = SubmitField('Create')