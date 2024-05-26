from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from wtforms.fields import DateTimeLocalField, IntegerField
from wtforms.validators import Optional, NumberRange

class OylamaForm(FlaskForm):
    question = StringField('Question', validators=[DataRequired(), Length(max=100)])
    options = TextAreaField('Options', validators=[DataRequired(), Length(max=500)])
    group_id = SelectField('Group', coerce=int, validators=[DataRequired()])
    days = IntegerField('Days', validators=[NumberRange(min=0)])
    hours = IntegerField('Hours', validators=[NumberRange(min=0, max=23)])
    minutes = IntegerField('Minutes', validators=[NumberRange(min=0, max=59)])
    submit = SubmitField('Create Poll')

class EmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

class GroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired(), Length(max=100)])
    emails = FieldList(FormField(EmailForm), min_entries=1, max_entries=10)  # 10 üyeye kadar sınırlandırdık
    submit = SubmitField('Create Group')