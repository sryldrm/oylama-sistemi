from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import json
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired,Length 

class OylamaForm(FlaskForm):
    question = StringField('Question',validators=[DataRequired(), Length(max=100)])
    options = TextAreaField('Options',validators=[DataRequired(),Length(max=500)])
    submit = SubmitField('Create Poll')


class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    members = db.relationship('Member', backref='group', lazy=True)
    polls = db.relationship('Poll', backref='group', lazy=True)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)

import random
import string

class Poll(db.Model):
    __tablename__ = 'poll'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(250), nullable=False)
    options = db.Column(db.Text, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    vote_code = db.Column(db.String(20), nullable=False, unique=True)
    end_time = db.Column(db.DateTime, nullable=True)

    def set_options(self, options):
        self.options = json.dumps(options)

    def get_options(self):
        return json.loads(self.options)

    @staticmethod
    def generate_vote_code():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=7))

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    choice = db.Column(db.Text, nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    is_admin = db.Column(db.Boolean, default=False)
    votes = db.relationship('Vote', backref='voter', lazy=True)
    groups = db.relationship('Member', backref='user', lazy=True)

def get_user_votes(user_id):
        return Vote.query.filter_by(user_id=user_id).all()

def get_user_groups(user_id):
    user_groups = Member.query.filter_by(user_id=user_id).all()
    groups = [group.group for group in user_groups]
    return groups

user_group = db.Table('user_group',  #Kullanıcıların gruplara üyeliklerini tutmak için. 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)
)