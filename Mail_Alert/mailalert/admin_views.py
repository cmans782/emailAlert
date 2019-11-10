from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_required
from flask import url_for, redirect, flash, render_template, current_app


class EmployeeView(ModelView):

    form_columns = ['hired_date', 'active', 'email',
                    'first_name', 'last_name', 'password', 'access', 'hall']

    column_searchable_list = ('first_name', 'last_name', 'email')

    form_choices = {
        'access': [
            ('DR', 'DR'),
            ('Building Director', 'Building Director'),
            ('Admin', 'Admin'),
        ]
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name):
        # check if the user is logged in
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        # return if user is logged in but not authorized
        return render_template('errors/403.html')


class StudentView(ModelView):

    form_columns = ['student_id', 'first_name', 'last_name', 'email',
                    'room_number', 'subscribed', 'phone_numbers', 'hall']

    column_searchable_list = ('first_name', 'last_name', 'email',
                              'room_number', 'student_id',)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.allowed('Building Director')

    def inaccessible_callback(self, name):
        # check if the user is logged in
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        # return if user is logged in but not authorized
        return render_template('errors/403.html')


class HallView(ModelView):

    form_columns = ['name', 'building_code']

    column_searchable_list = ('name', 'building_code')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name):
        # check if the user is logged in
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        # return if user is logged in but not authorized
        return render_template('errors/403.html')


class PackageView(ModelView):

    form_columns = ['status', 'description', 'delivery_date',
                    'picked_up_date', 'perishable', 'owner', 'hall', 'inputted', 'removed']

    column_searchable_list = ('description', 'delivery_date', 'picked_up_date')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.allowed('Building Director')

    def inaccessible_callback(self, name):
        # check if the user is logged in
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        # return if user is logged in but not authorized
        return render_template('errors/403.html')


class MessageView(ModelView):

    form_columns = ['content']

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name):
        # check if the user is logged in
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        # return if user is logged in but not authorized
        return render_template('errors/403.html')


class SentMailView(ModelView):

    form_columns = ['sent_date', 'cc_recipients',
                    'employee', 'message', 'student']

    def is_accessible(self):
        return current_user.is_authenticated and current_user.allowed('Building Director')

    def inaccessible_callback(self, name):
        # check if the user is logged in
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        # return if user is logged in but not authorized
        return render_template('errors/403.html')


class LoginView(ModelView):

    form_columns = ['login_date', 'logout_date', 'employee']

    def is_accessible(self):
        return current_user.is_authenticated and current_user.allowed('Building Director')

    def inaccessible_callback(self, name):
        # check if the user is logged in
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        # return if user is logged in but not authorized
        return render_template('errors/403.html')


class PhoneView(ModelView):

    form_columns = ['phone_number', 'assigned']

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name):
        # check if the user is logged in
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        # return if user is logged in but not authorized
        return render_template('errors/403.html')
