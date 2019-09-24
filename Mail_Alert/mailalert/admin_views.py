from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_login import current_user
from flask import url_for, redirect, flash, render_template


class EmployeeView(ModelView):
    # add CSRF protection
    form_base_class = SecureForm

    form_columns = ['hired_date', 'active', 'email',
                    'first_name', 'last_name', 'password', 'access', 'hall']

    form_choices = {
        'access': [
            ('DR', 'DR'),
            ('Building Director', 'Building Director'),
            ('Admin', 'Admin'),
        ]
    }

    def is_accessible(self):
        return current_user.is_admin()

    def inaccessible_callback(self, name):
        return render_template('errors/403.html')


class StudentView(ModelView):
     # add CSRF protection
    form_base_class = SecureForm

    form_columns = ['student_id', 'first_name', 'last_name',
                    'email', 'room_number', 'phone_number', 'hall']

    def is_accessible(self):
        return current_user.is_admin()

    def inaccessible_callback(self, name):
        return render_template('errors/403.html')


class HallView(ModelView):
     # add CSRF protection
    form_base_class = SecureForm

    form_columns = ['name']

    def is_accessible(self):
        return current_user.is_admin()

    def inaccessible_callback(self, name):
        return render_template('errors/403.html')


class PackageView(ModelView):
     # add CSRF protection
    form_base_class = SecureForm

    form_columns = ['status', 'description', 'delivery_date',
                    'picked_up_date', 'perishable', 'owner', 'hall', 'inputted', 'removed']

    def is_accessible(self):
        return current_user.is_admin()

    def inaccessible_callback(self, name):
        return render_template('errors/403.html')


class MessageView(ModelView):
     # add CSRF protection
    form_base_class = SecureForm

    form_columns = ['content']

    def is_accessible(self):
        return current_user.is_admin()

    def inaccessible_callback(self, name):
        return render_template('errors/403.html')


class SentMailView(ModelView):
     # add CSRF protection
    form_base_class = SecureForm

    form_columns = ['sent_date', 'cc_recipients', 'employee', 'message']

    def is_accessible(self):
        return current_user.is_admin()

    def inaccessible_callback(self, name):
        return render_template('errors/403.html')


class LoginView(ModelView):
     # add CSRF protection
    form_base_class = SecureForm

    form_columns = ['login_date', 'logout_date', 'employee']

    def is_accessible(self):
        return current_user.is_admin()

    def inaccessible_callback(self, name):
        return render_template('errors/403.html')
