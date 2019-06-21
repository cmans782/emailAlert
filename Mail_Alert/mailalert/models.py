from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from mailalert import db, login_manager
from flask_login import UserMixin
from flask import current_app
from datetime import datetime

@login_manager.user_loader
def load_user(id):
    return Employee.query.get(int(id))


class Employee(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    workinghall = db.Column(db.String(2), nullable=False)
    password = db.Column(db.String(60), nullable=False)

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


    def __repr__(self):
        return f"Employee('{self.email}', '{self.fname}', '{self.lname}', '{self.workinghall}')"

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    roomNum = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(100), nullable=False, default="Active")
    description = db.Column(db.String(250), nullable=False)
    delivery_date = db.Column(db.DateTime, nullable=False, default=datetime.now)


# class Student(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100), unique=True, nullable=False)
#     userID = db.Column(db.String(9), unique=True, nullable=False)
#     fname = db.Column(db.String(100), nullable=False)
#     lname = db.Column(db.String(100), nullable=False)
#     hall = db.Column(db.String(2), nullable=False)
#     room = db.Column(db.String(6), nullable=False)
#     phoneNumber = db.Column(db.String(15))

#     def __repr__(self):
#         return f"Student('{self.fname}', '{self.lname}', '{self.username}', '{self.userID}', '{self.hall}', '{self.room}', '{self.phoneNumber}')"

