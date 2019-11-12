
from flask_mail import Message
from mailalert import mail
from flask import url_for, render_template
from mailalert.models import Student


def send_new_package_email(student, num_packages):
    msg = Message('Kutztown Package Update',
                  sender='KutztownMail@gmail.com',
                  recipients=[student.email])

    # gbvw picks up their mail in roth
    hall = 'Rothermel' if student.hall.building_code == 'GW' else student.hall.name

    msg.html = render_template('new_package_email.html', num_packages=num_packages,
                               student=student, hall=hall)
    mail.send(msg)


def string_to_bool(s):
    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        return ValueError


def parse_name(name):
    """
    parse out the students first and last name.
    if the length of name is greater than 2, we assume
    that the student could have multiple first names along 
    with multiple last names  

    Parameters:
    name (string):

    Returns:
    fname - first name
    lname - last name
    """

    name_list = name.split()
    if len(name_list) == 2:
        fname, lname = name.split()

    # Find in the database students that have the same first name
    # as fname in the variable name. if this returns students,
    # append the next word in the list to fname and search. Keep
    # doing this until students returns none. When students returns
    # None we now knwo that the previous fname was the students first name.
    # we can then figure out the students last name with this information
    elif len(name_list) > 2:
        # assign the first element in the list to fname
        fname = name_list[0]
        i = 1
        # build fname
        while True:
            fname = fname + ' ' + name_list[i]
            student = Student.query.filter(
                Student.first_name.contains(fname)).all()
            if not student:
                # no students were found so we know the
                # previous fname was their first name
                break
            i += 1

        # convert fname to list so we can remove
        # the last element appended to it
        fname = fname.split(' ')
        del fname[-1]
        # convert back to a string
        fname = ' '.join(fname)

        # Now build last name starting at the same index
        lname = name_list[i]
        i += 1
        while i < len(name_list):
            lname = lname + ' ' + name_list[i]
            i += 1
    return fname.title(), lname.title()
