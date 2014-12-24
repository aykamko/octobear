from mongokit import Document, Connection, IS, ObjectId
import datetime
import json

config = json.load(open('../config.json', 'r'));
con = Connection()

def sid_validator(value):
    sid = re.compile(r'[0-9]')
    return bool(sid.match(value))
def email_validator(value):
    email = re.compile(r'(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)',re.IGNORECASE)
    return bool(email.match(value))
def grade_validator(grade_ids):
    for id in grade_ids:
        if not con.Grade.find_one({'_id': id}):
            return False
    return True

@con.register
class Member(Document):
    __collection__ = 'members'
    __database__ = config['course_name']
    structure = {
        'sid': basestring,
        'name': basestring,
        'email': basestring,
        'github': basestring,
        'registered': bool,
        'date_registered': datetime.datetime,
        'role': IS(0, 1, 2, 3), # 0: student; 1: reader; 2: ta; 3: instructor
        'grades': [ObjectId]
    }
    validators = {
        'sid': sid_validator,
        'email': email_validator,
        'grades': grade_validator
    }
    required_fields = ['sid']
    default_values = {'role': 0, 'registered': False}

@con.register
class Assignment(Document):
    __collection__ = 'assignments'
    __database__ = config['course_name']
    structure = {
        'name': basestring,
        'max_score': int,
        'weight': float
    }
    required_fields = ['name', 'max_score']

@con.register
class Grade(Document):
    __collection__ = 'grades'
    __database__ = config['course_name']
    structure = {
        'assignment': Assignment,
        'student': Member,
        'score': int,
        'grader': Member,
        'comments': basestring
    }
    required_fields = ['assignment', 'student']
