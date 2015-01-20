from mongokit import Document, IS, ObjectId, Set
import datetime
import json
import re

from .. import config
from . import connection

"""
validators
"""
def email_validator(value):
    email = re.compile(r'(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)',re.IGNORECASE)
    return bool(email.match(value))

def or_validator(*validator_list):
    def validator(obj):
        return any([validator(obj) for validator in validator_list])
    return validator

def id_class_validator(_class):
    def validator(obj_id):
        return bool(connection[_class.__name__].find_one({'_id': obj_id}))
    return validator

def id_collection_class_validator(_class):
    def validator(id_set):
        for obj in connection[_class.__name__].find({'_id': {'$in': list(id_set)}}):
            if type(obj) != _class:
                return False
        return True
    return validator

"""
schemas
"""
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
        'grades': Set(ObjectId), # Set(Grade)
        'group': ObjectId # Group
    }
    required_fields = ['sid', 'role', 'registered']
    default_values = {'role': 0, 'registered': False}
    indexes = [
        {
            'fields': 'sid',
            'unique': True,
            'ttl': 0
        }
    ]

class Group(Document):
    __collection__ = 'groups'
    __database__ = config['course_name']
    structure = {
        'name': basestring,
        'members': Set(ObjectId), # Member
        'grades': Set(ObjectId) # Grade
    }
    required_fields = ['name']
    indexes = [
        {
            'fields': 'name',
            'unique': True,
            'ttl': 0
        }
    ]

class Account(Document):
    __collection__ = 'accounts'
    __database__ = config['course_name']
    structure = {
        'login': basestring,
        'assigned': bool
    }
    required_fields = ['login', 'assigned']
    default_values = {'assigned': False}
    indexes = [
        {
            'fields': 'login',
            'unique': True,
            'ttl': 0
        }
    ]

class Assignment(Document):
    __collection__ = 'assignments'
    __database__ = config['course_name']
    structure = {
        'name': basestring,
        'max_score': float,
        'weight': float
    }
    required_fields = ['name', 'max_score']
    indexes = [
        {
            'fields': 'name',
            'unique': True,
            'ttl': 0
        }
    ]

class Grade(Document):
    __collection__ = 'grades'
    __database__ = config['course_name']
    structure = {
        'assignment': ObjectId, # Assignment
        'owner': ObjectId, # Member OR Group
        'group': bool,
        'score': float,
        'grader': ObjectId, # Member
        'comments': basestring
    }
    required_fields = ['assignment', 'owner']
    indexes = [
        {
            'fields': ['assignment', 'owner'],
            'unique': True,
            'ttl': 0
        }
    ]

    def add_grade_to_student(self, student_id):
        student = connection.Member.find_one({'_id': student_id})
        student['grades'].add(self['_id'])
        student.save()

    def save(self, uuid=False, validate=None, safe=True, *args, **kwargs):
        Document.save(self, uuid, validate, safe, *args, **kwargs)

        owner_id = self['owner']
        if self['group']:
            group = connection.Group.find_one({'_id': owner_id})
            group['grades'].add(self['_id'])
            group.save()
            student_ids = group['members']
            for _id in student_ids:
                self.add_grade_to_student(_id)
        else:
            self.add_grade_to_student(owner_id)

"""
Validators have to be assigned after class definition because of Mongokit's
eval procedure
"""
Member.validators = {
    'email': email_validator,
    'grades': id_collection_class_validator(Grade),
    'group': id_class_validator(Group)
}
Group.validators = {
    'members': id_collection_class_validator(Member),
    'grades': id_collection_class_validator(Grade)
}
Grade.validators = {
    'assignment': id_class_validator(Assignment),
    'owner': or_validator(id_class_validator(Member), id_class_validator(Group)),
    'grader': id_class_validator(Member)
}

connection.register([Member, Group, Account, Assignment, Grade])
