from mailalert import db

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    userID = db.Column(db.String(9), unique=True, nullable=False)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    hall = db.Column(db.String(2), nullable=False)
    room = db.Column(db.String(6), nullable=False)
    phoneNumber = db.Column(db.String(15))

    def __repr__(self):
        return f"Student('{self.fname}', '{self.lname}', '{self.username}', '{self.userID}', '{self.hall}', '{self.room}', '{self.phoneNumber}')"

class DR(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    workinghall = db.Column(db.String(2), nullable=False)
