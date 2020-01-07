import os
from flask import render_template, flash, redirect, url_for, request
from flask import send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from models import Paper, Submission
from forms import LoginForm, RegistrationForm, ConferenceForm, SectionForm, SearchForm, AddParkingSpotForm
from models import User, Conference, Section, SectionUser, UserPaperQualifier, ConferenceUser, Paper, ParkingSpot
from extensions import db
from utils import requires_roles
from app import app


@app.route('/')
@app.route('/home')
@login_required
def home():
    # todo maybe replace home.html with parking spot page
    return render_template('home.html', title='Home Page')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')

        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data, name=form.name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route('/proposal/submit', methods=['GET', 'POST'])
@login_required
@requires_roles('admin', 'author')
def submit_proposal():
    if request.method == 'POST':
        title = request.form['title']
        abstract = request.files['abstract']
        full_paper = request.files['full_paper']
        paper = Paper(title=title)
        db.session.add(paper)
        db.session.commit()
        abstract_name = str(paper.id) + 'abstract.' + abstract.filename.split('.')[-1]
        full_paper_name = str(paper.id) + 'full_paper.' + full_paper.filename.split('.')[-1]
        abstract.save(os.path.join(
            app.config['UPLOAD_PROPOSALS_FOLDER'], abstract_name))
        full_paper.save(os.path.join(
          app.config['UPLOAD_PROPOSALS_FOLDER'], full_paper_name))
        paper.abstract_name = abstract_name
        paper.full_paper_name = full_paper_name
        db.session.commit()
        submission = Submission(paper_id=paper.id, user_id=current_user.id)
        db.session.add(submission)
        db.session.commit()
    return render_template('submit_proposal.html', title='Submit Proposal')


@app.route('/proposals/<filename>')
@login_required
@requires_roles('admin', 'author', 'reviewer', 'participant')
def proposal_file(filename):
    return send_from_directory(app.config['UPLOAD_PROPOSALS_FOLDER'], filename)


@app.route('/conference', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def conference():
    form = ConferenceForm()

    if form.validate_on_submit():
        conference = Conference(name=form.name.data, startDate=form.startDate.data, endDate=form.endDate.data)
        db.session.add(conference)
        db.session.commit()

        flash('The new Conference has been added')
        return redirect(url_for('home'))

    return render_template('conference.html', title='Create Conference', form=form)

@app.route('/section', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def section():
    form = SectionForm()

    if form.validate_on_submit():
        conferenceId = Conference.query.filter_by(name=form.conference.data[0]).first().id
        speakerId = User.query.filter_by(name=form.data['speaker']).first().id
        paperId = Paper.query.filter_by(title=form.data['paper']).first().id
        section = Section(name=form.name.data, startDate=form.startDate.data, endDate=form.endDate.data,
                          conferenceId=conferenceId, paperId=paperId, speakerId=speakerId)
        db.session.add(section)
        db.session.commit()

        userId = User.query.filter_by(name=form.sessionChair.data).first().id
        sectionUser = SectionUser(userId=userId, sectionId=section.id)
        db.session.add(sectionUser)
        db.session.commit()

        flash('The new Section has been added')
        return redirect(url_for('home'))

    return render_template('section.html', title='Add Section', form=form)


@app.route('/proposals')
@login_required
@requires_roles('admin', 'reviewer')
def proposal_page():
    cursor = db.engine.raw_connection().cursor()
    cursor.execute('select * from papers')
    data = cursor.fetchall()  # data from database
    return render_template('proposals.html', value=data)


@app.route('/proposal-evaluate', methods=['POST'])
@login_required
@requires_roles('admin', 'reviewer')
def proposal_evaluate():
    user_id = int(current_user.id)
    paper_id = int(request.form['paper_id'])
    qualifier = str(request.form['qualifier'])
    if qualifier == '':
        return 'Error'
    user_paper_qualifier = \
        UserPaperQualifier.query.filter_by(user_id=user_id, paper_id=paper_id)
    if user_paper_qualifier.count() > 0:
        user_paper_qualifier.first().qualifier = qualifier
    else:
        user_paper_qualifier = UserPaperQualifier(user_id=user_id,
                                                  paper_id=paper_id,
                                                  qualifier=qualifier)
        db.session.add(user_paper_qualifier)
    db.session.commit()
    return "OK"


@app.route('/conferences')
@login_required
def conferences():
    cursor = db.engine.raw_connection().cursor()
    cursor.execute('select * from conferences')
    conferences = cursor.fetchall()
    conferencesUser = Conference.query.filter(
        Conference.users.any(username=current_user.username)).all()
    conferencesUserDict = {}
    data = []

    if len(conferencesUser) == 0:
        data = [conference + (False,) for conference in conferences]
    else:
        for conference in conferencesUser:
            conferencesUserDict[conference.id] = conference.name
        for conference in conferences:
            if conference[0] in conferencesUserDict.keys():
                data.append((conference + (True,)))
            else:
                data.append((conference + (False,)))

    return render_template('conferences.html', value=data)


@app.route('/attend-conference/<conferenceId>')
@login_required
def attend_conference(conferenceId):
    conferenceUser = ConferenceUser(userId=current_user.id, conferenceId=conferenceId)
    db.session.add(conferenceUser)
    db.session.commit()

    return redirect(url_for('conferences'))


@app.route('/unattend-conference/<conferenceId>')
@login_required
def unattend_conference(conferenceId):
    ConferenceUser.query.filter_by(userId=current_user.id, conferenceId=conferenceId).delete()
    db.session.commit()

    return redirect(url_for('conferences'))


@app.route('/sections/<conferenceId>')
@login_required
def sectionsForConference(conferenceId):
    sections = Section.query.filter_by(conferenceId=conferenceId).all()
    conferenceName = Conference.query.filter_by(id=conferenceId).first().name
    data = []

    for section in sections:
        paper = Paper.query.filter_by(id=section.paperId).first()
        speaker = User.query.filter_by(id=section.speakerId).first()
        sectionUsers = SectionUser.query.filter_by(sectionId=section.id).all()
        sessionChair = None

        for sectionUser in sectionUsers:
            user = User.query.filter_by(id=sectionUser.userId).first()

            for role in user.roles:
                if role.name == 'admin':
                    sessionChair = user.name
                    break

        data.append((section.name, speaker.name, sessionChair,
                     section.startDate, section.endDate,
                     paper.abstract_name, paper.full_paper_name))

    return render_template('sections_for_conference.html', value=data, conference=conferenceName)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()

    if form.validate_on_submit():
        city = form.city.data
        startDate = form.startDate.data
        endDate = form.endDate.data
        # todo implement parking_spots.html
        return redirect(url_for('parking_spots.html', city=city, startDate=startDate, endDate=endDate))

    return render_template('search.html', title='Search', form=form)


@app.route('/manage-spots', methods=['GET', 'POST'])
@login_required
def manage_spots():
    cursor = db.engine.raw_connection().cursor()
    cursor.execute('select * from parking_spots')
    userSpots = ParkingSpot.query.filter_by(idUser=current_user.id).all()
    data = userSpots

    return render_template('manage_spots.html', title='Manage spots', value=data)


@app.route('/add-parking-spot', methods=['GET', 'POST'])
@login_required
def add_parking_spot():
    form = AddParkingSpotForm()

    if form.validate_on_submit():
        parkingSpot = ParkingSpot(name=form.name.data, city=form.city.data, address=form.address.data,
                                  idUser=current_user.id)
        db.session.add(parkingSpot)
        db.session.commit()

        flash('The new Parking Spot has been added')
        return redirect(url_for('manage_spots'))

    return render_template('add_parking_spot.html', title='Add Parking Spot', form=form)
