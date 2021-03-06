from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from mailalert import db, login_manager
from flask_login import UserMixin
from flask import current_app
from datetime import datetime

ACCESS = {
    'None': 0,
    'DR': 1,
    'Building Director': 2,
    'Admin': 3
}


@login_manager.user_loader
def load_user(id):
    return Employee.query.get(int(id))


class Employee(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    hired_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    end_date = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)
    reset_password = db.Column(db.Boolean, default=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    access = db.Column(db.String, nullable=False, default="DR")
    hall_id = db.Column(db.Integer, db.ForeignKey('hall.id'))
    logins = db.relationship('Login', backref='employee')
    sent_mail = db.relationship('SentMail', backref='employee')
    inputted_packages = db.relationship(
        'Package', foreign_keys='[Package.employee_input_id]', backref='inputted')
    removed_packages = db.relationship(
        'Package', foreign_keys='[Package.employee_remove_id]', backref='removed')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Employee.query.get(user_id)

    def is_admin(self):
        return self.access == 'Admin'

    def allowed(self, access_level):
        return ACCESS[self.access] >= ACCESS[access_level]

    def __repr__(self):
        return f"Employee('{self.first_name + ' ' + self.last_name}', '{self.email}', '{self.hall}', '{self.access}')"


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    student_id = db.Column(db.String(9), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    room_number = db.Column(db.String(6), nullable=False)
    subscribed = db.Column(db.Boolean, default=True)
    hall_id = db.Column(db.Integer, db.ForeignKey('hall.id'))
    packages = db.relationship('Package', backref='owner')
    sent_mail = db.relationship('SentMail', backref='student')
    phone_numbers = db.relationship(
        'Phone', secondary='assigned', backref=db.backref('assigned', lazy='dynamic'))

    def __repr__(self):
        return f"Student('{self.first_name + ' ' + self.last_name}', '{self.email}','{self.student_id}', '{self.room_number}')"


class Hall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    building_code = db.Column(db.String(100), unique=True, nullable=False)
    students = db.relationship('Student', backref='hall')
    employees = db.relationship('Employee', backref='hall')
    packages = db.relationship('Package', backref='hall')

    def __repr__(self):
        return f"Hall('{self.name}', '{self.building_code}')"


class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(100), nullable=False, default="Active")
    description = db.Column(db.String(250), nullable=False)
    delivery_date = db.Column(
        db.DateTime, nullable=False, default=datetime.now)
    picked_up_date = db.Column(db.DateTime)
    perishable = db.Column(db.Boolean, default=False, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    phone_id = db.Column(db.Integer, db.ForeignKey('phone.id'))
    hall_id = db.Column(db.Integer, db.ForeignKey('hall.id'))
    employee_input_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    employee_remove_id = db.Column(db.Integer, db.ForeignKey('employee.id'))

    def __repr__(self):
        return f"Package('{self.status}', '{self.description}', '{self.delivery_date}', \
                        '{self.picked_up_date}', '{self.perishable}')"


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), unique=True, nullable=False)
    sent_mail = db.relationship('SentMail', backref='message')

    def __repr__(self):
        return f"Message('{self.content}')"


class SentMail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sent_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    cc_recipients = db.Column(db.String(250))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'))

    def __repr__(self):
        return f"SentMail({self.sent_date}', '{self.cc_recipients}')"


class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    logout_date = db.Column(db.DateTime)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))

    def __repr__(self):
        return f"Login('{self.login_date}', '{self.logout_date}')"


class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(15))
    packages = db.relationship('Package', backref='phone')

    def __repr__(self):
        return f"Phone('{self.phone_number}')"


assigned = db.Table('assigned',
                    db.Column('student_id', db.Integer,
                              db.ForeignKey('student.student_id')),
                    db.Column('phone_id', db.Integer,
                              db.ForeignKey('phone.id'))
                    )
