from mongokit import Document, IS, ObjectId, Set
import datetime
import json
import re

from .. import config
from . import connection

def email_validator(value):
    email = re.compile(r'(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)',re.IGNORECASE)
    return bool(email.match(value))
def grade_validator(grade_ids):
    for grade_obj in connection.Grade.find({'_id': {'$in': list(grade_ids)}}):
        if type(grade_obj) != Grade:
            return False
    return True
def id_class_validator(_class):
    def validator(obj_id):
        return bool(connection[_class.__name__].find_one({'_id': obj_id}))
    return validator

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
        'grades': Set(ObjectId) # Grade
    }
    validators = {
        'email': email_validator,
        'grades': grade_validator
    }
    required_fields = ['sid', 'role', 'registered']
    default_values = {'role': 0, 'registered': False}

@connection.register
class Account(Document):
    __collection__ = 'accounts'
    __database__ = config['course_name']
    structure = {
        'account': basestring,
        'assigned': bool
    }
    required_fields = ['account', 'assigned']
    default_values = {'assigned': False}

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
        'assignment': ObjectId, # Assignment
        'student': ObjectId, # Member
        'score': int,
        'grader': ObjectId, # Member
        'comments': basestring
    }
    validators = {
        'assignment': id_class_validator(Assignment),
        'student': id_class_validator(Member),
        'grader': id_class_validator(Member)
    }
    required_fields = ['assignment', 'student']

    def save(self, uuid=False, validate=None, safe=True, *args, **kwargs):
        Document.save(self, uuid, validate, safe, *args, **kwargs)
        student_id = self['student']
        student = connection.Member.find_one({'_id': student_id})
        student['grades'].add(self['_id'])
        student.save()
