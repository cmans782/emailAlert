from flask_admin.contrib.sqla import ModelView


class EmployeeView(ModelView):
    form_columns = ['hired_date', 'end_date', 'email',
                    'fname', 'lname', 'password', 'access', 'hall']


class StudentView(ModelView):
    form_columns = ['student_id', 'fname', 'lname',
                    'email', 'room_number', 'phone_number', 'hall']


class HallView(ModelView):
    form_columns = ['name']


class PackageView(ModelView):
    form_columns = ['status', 'description', 'delivery_date',
                    'picked_up_date', 'perishable', 'owner', 'hall', 'inputted', 'removed']


class MessageView(ModelView):
    form_columns = ['content']


class SentMailView(ModelView):
    form_columns = ['sent_date', 'cc_recipients', 'employee', 'message']


class LoginView(ModelView):
    form_columns = ['login_date', 'logout_date', 'employee']
