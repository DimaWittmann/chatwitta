from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.socketio import emit, join_room, leave_room
from app import app, lm, db, socketio
from forms import LoginForm, RegistrationForm, RoomForm
from models import User, Channel, Message
import datetime
from sqlalchemy import desc



@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = RoomForm()
    if form.validate_on_submit():
        rooms = Channel.query.filter(Channel.name.like('%' + form.name.data + '%')).order_by(desc(Channel.last_activity)).limit(10).all()
    else:
        rooms = Channel.query.order_by(desc(Channel.last_activity)).limit(10).all()
    return render_template('index.html', title='Chatwilla', rooms=rooms, form=form)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.login.data).first()
        if user is None:
            flash('Invalid login')    
        elif user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        else:
            flash('Invalid password')
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():    
    flash('Bye!')
    logout_user()
    return redirect(url_for('index'))


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            name=form.login.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now login.')
        return redirect(url_for('login'))
    return render_template('registration.html', title='Registration', form=form)

@app.route('/create_room', methods=['GET', 'POST'])
@login_required
def create_room():
    form = RoomForm()
    if form.validate_on_submit():
        room = Channel(name=form.name.data, creator=current_user)
        db.session.add(room)
        db.session.commit()
        flash('New room created')
        return redirect(url_for('room', roomname=room.name))
    return render_template('create_room.html', title='New room', form=form)
    
    
@app.route('/room/<roomname>')
@login_required
def room(roomname):
    room = Channel.query.filter_by(name=roomname).first()

    try:
        messages = room.messages.order_by(Message.id.desc()).all()
    except:
        messages = []
    return render_template('chat.html', title=room.name, messages=messages, room=room)
    

@socketio.on('connect', namespace='/chat')
def test_connect():
    print('Client connected')
    

@socketio.on('disconnect', namespace='/chat')
def test_disconnect():
    leave_room(session['room'])
    session['room'] = None
    print('Client disconnected')



@socketio.on('join', namespace='/chat')
def join(message):
    join_room(message['room'])
    session['room'] = message['room']
    emit('response', { 'data' : current_user.name + ' is connected to ' + message['room'] }, room=message['room'])
    

@socketio.on('message', namespace='/chat')
def receive(message):
    channel = Channel.query.filter_by(name=message['room']).first()
    msg = Message(
        text = message['data'],
        timestamp = datetime.datetime.utcnow(),
        user = current_user,
        channel = channel)
    db.session.add(msg)
    db.session.commit()
    channel.last_activity = msg.timestamp
    db.session.add(channel)
    db.session.commit()
    emit('message', { 'data' : message['data'], 'username' : msg.user.name, 'time' : msg.timestamp.strftime("%m-%d %H:%M")
, 'avatar' : msg.user.avatar(50) }, room=message['room'])
    
    
    
@socketio.on('leave', namespce='/chat')
def leave(message):
    leave_room(session['room'])
    emit('response', { 'data' : user.name + ' leave ' + session['room']}, room=session['room'])
    session['room'] = None



@app.before_request
def before_request():
    g.user = current_user



@lm.user_loader
def load_user(id):
    return User.query.get(int(id))



