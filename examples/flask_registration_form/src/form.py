from flask_wtf import Form
from wtforms.fields import StringField
from wtforms.validators import DataRequired, Email, ValidationError
import re

def github_validator(form, field):
    if not bool(re.match(r"[a-zA-Z0-9][a-zA-Z0-9\-]*$", field.data)):
        raise ValidationError('Invalid github username.')

class RegistrationForm(Form):
    sid = StringField(u'Student ID', validators=[DataRequired()])
    name = StringField(u'Full Name', validators=[DataRequired()])
    email = StringField(u'Email', validators=[DataRequired(), Email()])
    github = StringField(u'Github Handle', validators=[DataRequired(), github_validator])
