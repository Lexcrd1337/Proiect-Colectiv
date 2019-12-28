from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms.fields.html5 import DateField
from datetime import datetime
from models import User, Conference, Paper, UserPaperQualifier


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ConferenceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    startDate = StringField('Start Date', validators=[DataRequired()])
    endDate = StringField('End Date', validators=[DataRequired()])
    submit = SubmitField('Create')

class SectionForm(FlaskForm):
    name = StringField('Section Name', validators=[DataRequired()])
    startDate = StringField('Section Start Date', validators=[DataRequired()])
    endDate = StringField('Section End Date', validators=[DataRequired()])

    papers = Paper.query.all()
    acceptedPapers = []

    for paper in papers:
        qualifiers = UserPaperQualifier.query.filter_by(paper_id=paper.id).all()
        numberOfAccepts = 0
        numberOfRejects = 0

        for qualifier in qualifiers:
            if "accept" in qualifier.qualifier:
                numberOfAccepts += 1
            elif "reject" in qualifier.qualifier:
                numberOfRejects += 1

        if len(qualifiers) >= 2 and (numberOfRejects == 0 or
             (numberOfRejects != 0 and numberOfAccepts != 0 and numberOfAccepts > numberOfRejects)):
            acceptedPapers.append(paper)

    paper = SelectField('Paper', choices=[(paper.title, paper.title) for paper in acceptedPapers])
    conferences = Conference.query.all()
    users = User.query.all()
    sessionChairs = []

    for user in users:
        for role in user.roles:
            if role.name == 'admin':
                sessionChairs.append(user)
                break

    speaker = SelectField('Speaker', choices=[(user.name, user.name) for user in users])
    conference = SelectMultipleField('Conference', choices=[(conference.name, conference.name)
                                                            for conference in conferences])
    sessionChair = SelectField('Session Chair', choices=[(sessionChair.name, sessionChair.name)
                                                         for sessionChair in sessionChairs])

    submit = SubmitField('Add')