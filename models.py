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

    roles = db.relationship('Role', secondary='user_roles',
                            backref=db.backref('users'))

    conferences = db.relationship('Conference', secondary='conferences_users',
                                  backref=db.backref('users'))

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

    def get_roles(self):
        roleNames = []
        roles = Role.query.filter(Role.users.any(username=self.username)).all()
        for role in roles:
            roleNames.append(role.name)
        return roleNames

    def has_role(self, *roles):
        for role in self.get_roles():
            if role in roles:
                return True
        return False


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey(
        'roles.id', ondelete='CASCADE'))


class Paper(db.Model):
    __tablename__ = 'papers'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False, server_default='')
    abstract_name = db.Column(db.String(255), server_default='', unique=True)
    full_paper_name = db.Column(db.String(255), server_default='', unique=True)


class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    paper_id = db.Column(db.Integer(), db.ForeignKey(
        'papers.id', ondelete='CASCADE'))


class UserPaperQualifier(db.Model):
    __tablename__ = 'qualifiers'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    paper_id = db.Column(db.Integer(), db.ForeignKey(
        'papers.id', ondelete='CASCADE'))
    qualifier = db.Column(db.String(255), nullable=False, server_default='')


class Conference(db.Model):
    __tablename__ = 'conferences'
    id = db.Column(db.Integer(), primary_key=True)

    name = db.Column(db.String(255), nullable=False, unique=True)
    startDate = db.Column(db.Date(), nullable=False,
                          default=datetime.today().strftime('%Y-%m-%d'))
    endDate = db.Column(db.Date(), nullable=False,
                        default=datetime.today().strftime('%Y-%m-%d'))

    sections = db.relationship('Section', uselist=False,
                               backref=db.backref('conferences'))


class Section(db.Model):
    __tablename__ = 'sections'
    id = db.Column(db.Integer(), primary_key=True)

    name = db.Column(db.String(255), nullable=False, unique=True)
    startDate = db.Column(db.Date(), nullable=False,
                          default=datetime.today().strftime('%Y-%m-%d'))
    endDate = db.Column(db.Date(), nullable=False,
                        default=datetime.today().strftime('%Y-%m-%d'))
    conferenceId = db.Column(db.Integer(), db.ForeignKey('conferences.id'))
    paperId = db.Column(db.Integer(), db.ForeignKey('papers.id'))
    speakerId = db.Column(db.Integer(), db.ForeignKey('users.id'))
    sectionUsers = db.relationship('SectionUser',
                                   backref=db.backref('sections'))


class SectionUser(db.Model):
    __tablename__ = 'sections_users'
    id = db.Column(db.Integer(), primary_key=True)
    userId = db.Column(db.Integer(),
                       db.ForeignKey('users.id', ondelete='CASCADE'))
    sectionId = db.Column(db.Integer(),
                          db.ForeignKey('sections.id', ondelete='CASCADE'))


class ConferenceUser(db.Model):
    __tablename__ = 'conferences_users'
    id = db.Column(db.Integer(), primary_key=True)
    userId = db.Column(db.Integer(),
                       db.ForeignKey('users.id', ondelete='CASCADE'))
    conferenceId = db.Column(db.Integer(),
                          db.ForeignKey('conferences.id', ondelete='CASCADE'))


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
