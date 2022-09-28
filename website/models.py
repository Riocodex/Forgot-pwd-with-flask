from . import db , create_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy.sql import func
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField , SubmitField
from wtforms.validators import DataRequired , Length , EqualTo , Email

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Books(db.Model):
    id=db.Column(db.Integer , primary_key=True)
    carBrand = db.Column(db.String(150))
    numberOfSeats =  db.Column(db.String(150))
    costs = db.Column(db.String(150))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    books = db.relationship('Books' , lazy = 'dynamic' , backref=db.backref('category' , lazy=True))
    
    def get_token(self , expires_sec = 300):
        serial = Serializer( create_app.config['SECRET_KEY'] , expires_in = expires_sec)
        return serial.dumps({'user_id':self.id}).decode('utf-8')
    
    @staticmethod
    def verify_token(token):
        serial = Serializer( create_app.config['SECRET_KEY'] )
        try:
            user_id = serial.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    
class ResetRequestForm(FlaskForm):
    email = StringField(label ='Email' , validators=[DataRequired()])
    submit = SubmitField(label='Reset Password' , validators=[DataRequired()])

class ResetPasswordForm(FlaskForm):
    password = PasswordField(label='Password' , validators=[DataRequired()])
    confirm_password = PasswordField(label = 'Confirm Password' , validators=[DataRequired()])
    submit = SubmitField(label='Change Password' , validators=[DataRequired()])
