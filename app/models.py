from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from hashlib import md5

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(24), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    _password_hash = db.Column(db.String(124))
    
    def __init__(self, email, name, password):
        self.email = email
        self.name = name
        self.password = password


    @property
    def password(self):
        raise AttributeError()
    @password.setter
    def password(self, password):
        self._password_hash = generate_password_hash(password)


    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' \
        + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)


    def verify_password(self, password):
        return check_password_hash(self._password_hash, password)


    def __repr__(self):
        return '<User %r>' % (self.name)


class Channel(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(24), index = True, unique = True)
    last_activity = db.Column(db.DateTime)
    
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref = db.backref('channels', lazy = 'dynamic'))


    def __init__(self, name, creator):
        self.name = name
        self.creator = creator


    def __repr__(self):
        return '<Channel %r>' % (self.name)

class Message(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref = db.backref('messages', lazy = 'dynamic'))
    
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
    channel = db.relationship('Channel', backref = db.backref('messages', lazy = 'dynamic'))

    def __init__(self, text, timestamp, user, channel):
        self.text = text
        self.timestamp = timestamp
        self.user = user
        self.channel = channel
        
    def __repr__(self):
        return '<Message %r %r %r %r>' % (self.text, self.timestamp, self.user, self.channel)
