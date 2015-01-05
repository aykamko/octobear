from flask_wtf import Form
from wtforms.fields import StringField
from wtforms.validators import DataRequired, Email

class RegistrationForm(Form):
    sid = StringField(u'Student ID', validators=[DataRequired()])
    name = StringField(u'Full Name', validators=[DataRequired()])
    email = StringField(u'Email', validators=[DataRequired(), Email()])
    github = StringField(u'Github Handle', validators=[DataRequired()])
