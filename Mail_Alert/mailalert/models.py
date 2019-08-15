from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from mailalert import db, login_manager
from flask_login import UserMixin
from flask import current_app
from datetime import datetime

ACCESS = {
    'DR': 0,
    'Building Director': 1,
    'Admin': 2
}


@login_manager.user_loader
def load_user(id):
    return Employee.query.get(int(id))


class Employee(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    hired_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    access = db.Column(db.String, nullable=False, default="DR")
    hall_id = db.Column(db.Integer, db.ForeignKey('hall.id'))

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
        return f"Employee('{self.hired_date}', '{self.email}', '{self.fname}', '{self.lname}', '{self.hall}', '{self.access}')"


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    userID = db.Column(db.String(9), unique=True, nullable=False)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(6), nullable=False)
    phoneNumber = db.Column(db.String(15))
    hall_id = db.Column(db.Integer, db.ForeignKey('hall.id'))
    package = db.relationship('Package', backref='owner')

    def __repr__(self):
        return f"Student('{self.email}','{self.userID}', '{self.fname}', '{self.lname}', '{self.room}', '{self.phoneNumber}')"


class Hall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    students = db.relationship('Student', backref='hall')
    employees = db.relationship('Employee', backref='hall')

    def __repr__(self):
        return f"Hall('{self.name}')"


class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(100), nullable=False, default="Active")
    description = db.Column(db.String(250), nullable=False)
    delivery_date = db.Column(
        db.DateTime, nullable=False, default=datetime.now)
    picked_up_date = db.Column(db.DateTime)
    dr = db.Column(db.String(100), nullable=False)
    perishable = db.Column(db.Boolean, default=False, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))

    def __repr__(self):
        return f"Package('{self.status}', '{self.description}', '{self.delivery_date}', \
                        '{self.picked_up_date}', '{self.dr}', '{self.perishable}', '{self.student_id}')"


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), unique=True, nullable=False)


class SentMail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    messageId = db.Column(db.Integer)
    recipient = db.Column(db.String(250), nullable=False)
    content = db.Column(db.String(250), nullable=False)
    sent_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    sender = db.Column(db.String(250), nullable=False)
