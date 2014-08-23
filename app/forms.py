from flask.ext.wtf import Form 
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from models import User

class LoginForm(Form):

    login = StringField('Login', description='Login', validators=[Required("Enter login"),\
        Length(4, 24)])
    password = PasswordField('Password', description='Password', validators=[Required("Enter password"), Length(8, 24)])
    remember_me = BooleanField('Remember me', default=False)
    

class RegistrationForm(Form):
    email = StringField('Email', description='Email', validators=[Required(), Length(1, 64), Email()])
    login = StringField('Login', description='Login', validators=[Required(), Length(4,24), \
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'Letters, numbers, dots or _')])
    password = PasswordField('Password', description='Password', validators=[Required(), EqualTo('password2', \
        message='Passwords do not match')])
    password2 = PasswordField('Confirm password', description='Confirm password', validators=[Required()])


    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


    def validate_login(self, field):
        if User.query.filter_by(name=field.data).first():
            raise ValidationError('Username already in use')


class RoomForm(Form):
    name = StringField('Room name', validators=[Required(), Regexp('^[A-Za-z0-9_.]*$', 0,'Letters, numbers, dots or _')])
    
