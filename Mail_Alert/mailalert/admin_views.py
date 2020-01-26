from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import render_template, current_app
from mailalert.filters import admin_datetime_filter
from flask_admin.model import typefmt
from datetime import date

MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
MY_DEFAULT_FORMATTERS.update({
    date: admin_datetime_filter
})


class EmployeeView(ModelView):

    form_columns = ['start_date', 'active', 'reset_password', 'email', 'first_name',
                    'last_name', 'password', 'access', 'hall']

    column_searchable_list = ('first_name', 'last_name', 'email')

    column_default_sort = ('start_date', True)

    # format time from utc to local time
    column_type_formatters = MY_DEFAULT_FORMATTERS

    form_choices = {
        'access': [
            ('DR', 'DR'),
            ('Building Director', 'Building Director'),
            ('Admin', 'Admin'),
        ]
    }

    # def is_accessible(self):
    #     return current_user.is_authenticated and current_user.is_admin()

    # def inaccessible_callback(self, name):
    #     # check if the user is logged in
    #     if not current_user.is_authenticated:
    #         return current_app.login_manager.unauthorized()
    #     # return if user is logged in but not authorized
    #     return render_template('errors/403.html')


class StudentView(ModelView):

    form_columns = ['student_id', 'first_name', 'last_name', 'email', 'room_number',
                    'subscribed', 'phone_numbers', 'hall', 'start_date', 'end_date', 'active']

    column_searchable_list = ('first_name', 'last_name', 'email',
                              'room_number', 'student_id',)

    column_default_sort = ('start_date', True)

    # format time from utc to local time
    column_type_formatters = MY_DEFAULT_FORMATTERS

    def is_accessible(self):
        return current_user.is_authenticated and current_user.allowed('Building Director')

    def inaccessible_callback(self, name):
        # check if the user is logged in
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        # return if user is logged in but not authorized
        return render_template('errors/403.html')


class HallView(ModelView):

    form_columns = ['name', 'building_code', 'active', 'end_date']

    column_searchable_list = ('name', 'building_code', 'active', 'end_date')

    # format time from utc to local time
    column_type_formatters = MY_DEFAULT_FORMATTERS

    # def is_accessible(self):
    #     return current_user.is_authenticated and current_user.is_admin()

    # def inaccessible_callback(self, name):
    #     # check if the user is logged in
    #     if not current_user.is_authenticated:
    #         return current_app.login_manager.unauthorized()
    #     # return if user is logged in but not authorized
    #     return render_template('errors/403.html')


class PackageView(ModelView):

    form_columns = ['package_number', 'status', 'description', 'delivery_date',
                    'picked_up_date', 'perishable', 'owner', 'hall', 'inputted', 'removed']

    column_searchable_list = ('description', 'delivery_date', 'picked_up_date')

    column_default_sort = ('delivery_date', True)

    # format time from utc to local time
    column_type_formatters = MY_DEFAULT_FORMATTERS

    def is_accessible(self):
        return current_user.is_authenticated and current_user.allowed('Building Director')

    def inaccessible_callback(self, name):
        # check if the user is logged in
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        # return if user is logged in but not authorized
        return render_template('errors/403.html')


class SentMailView(ModelView):

    form_columns = ['sent_date', 'employee', 'student']

    column_default_sort = ('sent_date', True)

    # format time from utc to local time
    column_type_formatters = MY_DEFAULT_FORMATTERS

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

    column_default_sort = ('login_date', True)

    # format time from utc to local time
    column_type_formatters = MY_DEFAULT_FORMATTERS

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


class UtilsView(ModelView):

    form_columns = ['semester', 'employment_code', 'active']

    column_default_sort = ('semester', True)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name):
        # check if the user is logged in
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        # return if user is logged in but not authorized
        return render_template('errors/403.html')


class CeleryView(ModelView):

    form_columns = ['name', 'date_done', 'status', 'message']

    column_default_sort = ('date_done', True)

    # format time from utc to local time
    column_type_formatters = MY_DEFAULT_FORMATTERS

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name):
        # check if the user is logged in
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        # return if user is logged in but not authorized
        return render_template('errors/403.html')
