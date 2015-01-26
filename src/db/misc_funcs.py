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
from ..github.github import github, GitHubApiError

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

# Redos every step in the github hookup process
# Idempotent
def redo_github(student):
    teamName, repoName = student['login'], student['login']
    try:
        github.createRepo(repoName)
        print "Created repo: " + repoName
    except GitHubApiError:
        # print "Repo exists: " + repoName
        pass

    try:
        teamID = github.createTeam(teamName)
        github.addTeamMembers(teamID, [student['github']])
        print "Created team: " + teamName
    except GitHubApiError:
        # print "Team exists: " + teamName
        pass

    github.createHook(repoName, config['jenkins_hook'])
    # print "Created hook"

    print "Finished student " + str(student['sid'])

def redo_everyone():
    for student in connection.Member.find():
        if student['registered'] and student['login']:
            redo_github(student)
        else:
            print "Skipped student" + str(student['sid'])

get_s = get_student
