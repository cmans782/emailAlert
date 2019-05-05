from mailalert import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(id):
    return Employee.query.get(int(id))


class Employee(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    workinghall = db.Column(db.String(2), nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Employee('{self.username}', '{self.fname}', '{self.lname}', '{self.workinghall}')"


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    userID = db.Column(db.String(9), unique=True, nullable=False)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    hall = db.Column(db.String(2), nullable=False)
    room = db.Column(db.String(6), nullable=False)
    phoneNumber = db.Column(db.String(15))

    def __repr__(self):
        return f"Student('{self.fname}', '{self.lname}', '{self.username}', '{self.userID}', '{self.hall}', '{self.room}', '{self.phoneNumber}')"

