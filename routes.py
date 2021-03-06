import os
from datetime import date
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from models import Booking
from forms import LoginForm, RegistrationForm, SearchForm, AddParkingSpotForm, AddTimeOffForm
from models import User, ParkingSpot, TimeOff, Notification
from extensions import db, cities
from app import app
from flask_mail import *


@app.route('/')
@app.route('/home')
@login_required
def home():
    return redirect(url_for('search'))


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
        user = User(username=form.username.data, email=form.email.data, name=form.name.data,
                    phoneNumber=form.phoneNumber.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        msg = Message(
            subject="Account Creation",
            sender=app.config.get("MAIL_USERNAME"),
            recipients=[form.email.data],
            body="Your account have been created! :)"
        )
        mail = Mail(app)
        mail.send(msg)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()

    if form.validate_on_submit():
        city = form.city.data
        startDate = form.startDate.data
        endDate = form.endDate.data
        return redirect(url_for('parking_spots', city=city, startDate=startDate, endDate=endDate))

    return render_template('search.html', title='Search', form=form, cities=cities)


@app.route('/parking-spots/<city>/<startDate>/<endDate>', methods=['GET', 'POST'])
@login_required
def parking_spots(city, startDate, endDate):
    timeOffs = TimeOff.query.filter(TimeOff.startDate <= startDate).filter(TimeOff.endDate >= endDate).all()
    data = []

    for timeOff in timeOffs:
        parkingSpot = ParkingSpot.query.filter_by(id=timeOff.idParkingSpot).first()

        if parkingSpot.city == city and parkingSpot.available:
            data.append((parkingSpot, timeOff))

    return render_template('parking_spots.html', title='Parking spots', value=data,
                           city=city, startDate=startDate, endDate=endDate)


@app.route('/user-details/<parkingSpotId>', methods=['GET'])
@login_required
def user_details(parkingSpotId):
    parkingSpot = ParkingSpot.query.filter_by(id=parkingSpotId).first()
    user = User.query.filter_by(id=parkingSpot.idUser).first()
    name = user.name
    email = user.email
    phoneNumber = user.phoneNumber

    return render_template('user_details.html', title='User Details', name=name, email=email, phoneNumber=phoneNumber)


@app.route('/book/<parkingSpotId>/<timeOffId>/<startDate>/<endDate>')
@login_required
def book(parkingSpotId, timeOffId, startDate, endDate):
    timeOff = TimeOff.query.filter_by(id=timeOffId).first()
    startDate = datetime.strptime(startDate, '%m-%d-%Y').date()
    endDate = datetime.strptime(endDate, '%m-%d-%Y').date()
    booking = Booking(startDate=startDate, endDate=endDate, idUser=current_user.id, idParkingSpot=parkingSpotId)

    if startDate > timeOff.startDate and endDate < timeOff.endDate:
        timeOff1 = TimeOff(startDate=timeOff.startDate, endDate=startDate, idParkingSpot=parkingSpotId)
        timeOff2 = TimeOff(startDate=endDate, endDate=timeOff.endDate, idParkingSpot=parkingSpotId)
        db.session.add(timeOff1)
        db.session.add(timeOff2)
        db.session.commit()
    elif startDate > timeOff.startDate and endDate == timeOff.endDate:
        timeOff3 = TimeOff(startDate=timeOff.startDate, endDate=startDate, idParkingSpot=parkingSpotId)
        db.session.add(timeOff3)
        db.session.commit()
    elif startDate == timeOff.startDate and endDate < timeOff.endDate:
        timeOff4 = TimeOff(startDate=endDate, endDate=timeOff.endDate, idParkingSpot=parkingSpotId)
        db.session.add(timeOff4)
        db.session.commit()
    else:
        make_parking_spot_unavailable(parkingSpotId)

    spotDetails = ParkingSpot.query.filter_by(id=parkingSpotId).first()
    city = spotDetails.city.split()
    address = spotDetails.address.split()
    cityInLink = ""
    adressInLink = ""
    for word in city:
        cityInLink = cityInLink + "+" + str(word)
    for word in address:
        adressInLink = adressInLink + str(word) + "+"
    adressInLink = adressInLink[:-1] + ','
    adressInLink = adressInLink + cityInLink
    print(adressInLink)

    msg = Message(
        subject="New Booking",
        sender=app.config.get("MAIL_USERNAME"),
        recipients=[current_user.email],
        body="You booked a parking spot in" + str(spotDetails.city) + " at address: " + str(spotDetails.address) +
             ". See the location in google maps here: https://www.google.com/maps/place/" + str(adressInLink) + "/"

    )
    mail = Mail(app)
    mail.send(msg)

    newMsg = Notification(idUser=current_user.id,
                          message="You booked a parking spot between: " + str(timeOff.startDate) + " - " + str(
                              timeOff.endDate) + ". An email with details was sent to you.",
                          msgType=2,
                          msgDate=date.today())

    db.session.add(newMsg)
    db.session.add(booking)
    db.session.delete(timeOff)
    db.session.commit()

    flash('You just booked a new parking spot!')
    return redirect(url_for('my_bookings'))


@app.route('/my-bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(idUser=current_user.id).all()
    data = []

    for booking in bookings:
        parkingSpot = ParkingSpot.query.filter_by(id=booking.idParkingSpot).first()
        data.append((parkingSpot, booking))

    return render_template('bookings.html', title='My Bookings', value=data)


@app.route('/inbox')
@login_required
def inbox():
    messages = Notification.query.filter_by(idUser=current_user.id).all()
    data = messages
    return render_template('inbox.html', value=data)


@app.route('/manage-spots', methods=['GET', 'POST'])
@login_required
def manage_spots():
    cursor = db.engine.raw_connection().cursor()
    cursor.execute('select * from parking_spots')
    userSpots = ParkingSpot.query.filter_by(idUser=current_user.id).all()
    dates = TimeOff.query.filter_by(idParkingSpot=ParkingSpot.id).all()
    data = userSpots
    data2 = dates
    return render_template('manage_spots.html', title='Manage spots', value=data, value2=data2)


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

    return render_template('add_parking_spot.html', title='Add Parking Spot', form=form, cities=cities)


@app.route('/remove-parking-spot/<parkingSpotId>')
@login_required
def remove_parking_spot(parkingSpotId):
    affected = Booking.query.filter_by(idParkingSpot=parkingSpotId).all()
    for entry in affected:
        newMsg = Notification(idUser=entry.idUser,
                              message="Your booking for the dates: " + str(entry.startDate) + " - " + str(
                                  entry.endDate) +
                                      " has been canceled because the parking " +
                                      "spot was removed by the owner.",
                              msgType=1,
                              msgDate=date.today())
        db.session.add(newMsg)
    ParkingSpot.query.filter_by(id=parkingSpotId).delete()

    db.session.commit()

    return redirect(url_for('manage_spots'))

@app.route('/remove-msg/<msgId>')
@login_required
def remove_msg(msgId):
    Notification.query.filter_by(id=msgId).delete()
    db.session.commit()
    return redirect(url_for('inbox'))


@app.route('/make-parking-spot-unavailable/<parkingSpotId>')
@login_required
def make_parking_spot_unavailable(parkingSpotId):
    parkingSpot = ParkingSpot.query.filter_by(id=parkingSpotId).first()
    timeOffs = TimeOff.query.filter_by(idParkingSpot=parkingSpotId)

    for timeOff in timeOffs:
        db.session.delete(timeOff)

    parkingSpot.available = False
    db.session.commit()

    return redirect(url_for('manage_spots'))


@app.route('/make-parking-spot-available/<parkingSpotId>')
@login_required
def make_parking_spot_available(parkingSpotId):
    return redirect(url_for('add_time_off', parkingSpotId=parkingSpotId))


@app.route('/add-time-off/<parkingSpotId>', methods=['GET', 'POST'])
@login_required
def add_time_off(parkingSpotId):
    form = AddTimeOffForm()

    if form.validate_on_submit():
        timeOff = TimeOff(startDate=form.startDate.data, endDate=form.endDate.data, idParkingSpot=parkingSpotId)
        parkingSpot = ParkingSpot.query.filter_by(id=parkingSpotId).first()
        parkingSpot.available = True
        # for deleting old time off
        TimeOff.query.filter_by(idParkingSpot=parkingSpotId).delete()
        affected = Booking.query.filter_by(idParkingSpot=parkingSpotId).all()
        for entry in affected:
            newMsg = Notification(idUser=entry.idUser,
                                  message="Your booking for the dates: " + str(entry.startDate) + " - " + str(
                                      entry.endDate) +
                                          " has been canceled because the parking " +
                                          "spot was updated. Please check the new dates and book again if it's still fine for you.",
                                  msgType=3,
                                  msgDate=date.today()
                                  )
            db.session.add(newMsg)
        Booking.query.filter_by(idParkingSpot=parkingSpotId).delete()
        db.session.add(timeOff)
        db.session.commit()

        return redirect(url_for('manage_spots'))

    return render_template('add_time_off.html', title='Add Time Off', form=form)
