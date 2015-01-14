#!/usr/bin/env python
import argparse
import pprint
import sys
from src.db.schema import connection, Assignment
from src import config

def get_assignment(name):
    return connection.Assignment.find_one({'name': name})

def create_assignment(name, max_score, weight=None):
    if get_assignment(name):
        raise Exception('Assignment {0} already exists!'.format(name))
    new = connection.Assignment()
    new['name'] = name
    new['max_score'] = int(max_score)
    if weight:
        new['weight'] = int(weight)
    new.save()
    return new

assignment_coll = connection[config['course_name']][Assignment.__collection__]
def delete_assignment(name):
    return assignment_coll.remove({'name': name})

def confirm(func, *func_args, **kwargs):
    prompt = kwargs.get('prompt')
    if not prompt:
        prompt = 'Confirm'

    prompt_base = '%s [%s]|%s: '
    if kwargs.get('default_resp'):
        prompt = prompt_base % (prompt, 'y', 'n')
    else:
        prompt = prompt_base % (prompt, 'n', 'y')

    while True:
        ans = raw_input(prompt)
        if not ans:
            if kwargs.get('default_resp'):
                return func(*func_args)
            return
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'Please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return func(*func_args)
        if ans == 'n' or ans == 'N':
            return

if __name__ == '__main__':
    actions = {
        'get': lambda x: get_assignment(x),
        'create': lambda x, y, z=None: create_assignment(x, y, z),
        'delete': lambda x: confirm(delete_assignment, x,
            prompt='Are you sure you want to delete this assignment?')
    }

    parser = argparse.ArgumentParser(
            description='Create and query assignments.')
    parser.add_argument('action',
            choices=actions.keys(),
            help='Action to perform with assignments.')
    parser.add_argument('args',
            nargs=argparse.REMAINDER)
    args = parser.parse_args()

    ret = actions[args.action](*args.args)
    if ret:
        pprint.pprint(ret, width=1)
    sys.exit(0)
