from mongokit import Document, IS, ObjectId
import datetime
import json
import re

from .. import config
from . import connection

def email_validator(value):
    email = re.compile(r'(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)',re.IGNORECASE)
    return bool(email.match(value))
def grade_validator(grade_ids):
    for grade_obj in connection.Grade.find({'_id': {'$in': grade_ids}}):
        if type(grade_obj) != Grade:
            return False
    return True

@connection.register
class Member(Document):
    __collection__ = 'members'
    __database__ = config['course_name']
    structure = {
        'sid': int,
        'login': basestring,
        'name': basestring,
        'email': basestring,
        'github': basestring,
        'registered': bool,
        'time_registered': datetime.datetime,
        'role': IS(0, 1, 2, 3), # 0: student; 1: reader; 2: ta; 3: instructor
        'grades': [ObjectId]
    }
    validators = {
        'email': email_validator,
        'grades': grade_validator
    }
    required_fields = ['sid']
    default_values = {'role': 0, 'registered': False}

@connection.register
class Assignment(Document):
    __collection__ = 'assignments'
    __database__ = config['course_name']
    structure = {
        'name': basestring,
        'max_score': int,
        'weight': float
    }
    required_fields = ['name', 'max_score']

@connection.register
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
