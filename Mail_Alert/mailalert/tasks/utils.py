from flask_mail import Message
from mailalert import mail
import pandas as pd
import io


def send_err_email(status, err, time, error_df):
    msg = Message(f'Roster Upload {status}',
                  sender='KutztownMail@gmail.com',
                  recipients=['tlentz1008@gmail.com'])
    if status == 'ERROR':
        msg.body = f'''{error_df['USERNAME'].count()} error(s) occurred while attempting to upload the student roster. 
Attached to this email is a file containing the students that failed to upload along with a short description of why. 
Please correct these errors so that we may insure that all student information is up to date.

please contact EMAILADDRESS if additional support is needed. 
'''
        msg.attach(filename='upload_errors.csv', data=export_csv(
            error_df), content_type='text/csv')
    else:
        msg.body = f'''The student roster failed to upload. Please correct this as soon as possible so that we may insure that all student information is up to date. 

Reason for Failure:
{err}

please contact EMAILADDRESS if additional support is needed. 
'''

    mail.send(msg)
    return


def export_csv(df):
    with io.StringIO() as buffer:
        df.to_csv(buffer, index=False)
        return buffer.getvalue()
