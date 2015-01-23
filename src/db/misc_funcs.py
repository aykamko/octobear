###############################################################################
#
#   WARNING
#
#   USE WITH CAUTION
#
###############################################################################
import os
from .schema import *
from .. import config, jprint, emailer
from ..github.github import github

accounts_coll = connection.Account.collection
members_coll = connection.Member.collection

def free_all_accounts():
    accounts_coll.update(
            {'assigned': True},
            {'$set': {'assigned': False}}
            )

def unregister_all_users():
    members_coll.update(
            {'registered': True},
            {'$set': {'registered': False}}
            )

def get_student(sid):
    s = connection.Member.find_one({'sid': sid})
    if not s:
        print 'No student found!'
    return s

def resend_registration_info(student):
    account_form = os.path.realpath('./account_forms') + ('/%s.pdf' % (student['login']))
    emailer.send_template(
            student['email'],
            '[{0}] Registered!'.format(config['course_name']),
            'registered.html',
            files=[account_form],
            user=student)

def regenerate_github(student):
    github.createEverything(
            student['login'],
            [student['github']],
            config['jenkins_hook'])

get_s = get_student
