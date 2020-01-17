from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db
from datetime import datetime
from app import login

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phoneNumber = db.Column(db.String(255), nullable=False, server_default='')
    password = db.Column(db.String(255), nullable=False, server_default='')
    name = db.Column(db.String(100), nullable=False, server_default='')


    def __init__(self, username, email, name, phoneNumber):
        self.username = username
        self.email = email
        self.name = name
        self.password = ''
        self.phoneNumber = phoneNumber

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)




class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    available = db.Column(db.Boolean(), nullable=False, default=False)
    idUser = db.Column(db.Integer(),
                       db.ForeignKey('users.id', ondelete='CASCADE'))

class TimeOff(db.Model):
    __tablename__ = 'time_offs'
    id = db.Column(db.Integer(), primary_key=True)
    startDate = db.Column(db.Date(), nullable=False,
                          default=datetime.today().strftime('%Y-%m-%d'))
    endDate = db.Column(db.Date(), nullable=False,
                        default=datetime.today().strftime('%Y-%m-%d'))
    idParkingSpot = db.Column(db.Integer(),
                              db.ForeignKey('parking_spots.id', ondelete='CASCADE'))

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer(), primary_key=True)
    startDate = db.Column(db.Date(), nullable=False,
                          default=datetime.today().strftime('%Y-%m-%d'))
    endDate = db.Column(db.Date(), nullable=False,
                        default=datetime.today().strftime('%Y-%m-%d'))
    idUser = db.Column(db.Integer(),
                       db.ForeignKey('users.id', ondelete='CASCADE'))
    idParkingSpot = db.Column(db.Integer(),
                              db.ForeignKey('parking_spots.id', ondelete='CASCADE'))


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer(), primary_key=True)
    idUser = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    message = db.Column(db.String(255), nullable=False)
    msgType = db.Column(db.INTEGER(), nullable=False)
    msgDate = db.Column(db.DATE(), nullable=False)