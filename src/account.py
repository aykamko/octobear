import string
import re
import logging
import itertools
import os
from os.path import dirname
from db.schema import connection, Account
from . import config

logger = logging.getLogger('Account')
account_coll = connection[config['course_name']][Account.__collection__]
account_forms_directory = os.path.join(dirname(dirname(__file__)), "account-forms")

def generate_login_list(num, minimum_length=2):
    accounts = []
    alph = string.lowercase
    non_reserved = lambda account: account[0] not in ('t', 'r', 'l') # TRL
    for length in itertools.count(minimum_length):
        accounts.extend(map(''.join, filter(non_reserved, itertools.product(alph, repeat=length))))
        if len(accounts) >= num:
            return accounts[:num]

def register_num_accounts(num, minimum_length=2):
    bulk = account_coll.initialize_ordered_bulk_op()
    for account_str in generate_login_list(num, minimum_length=minimum_length):
        account = connection.Account()
        account['login'] = account_str
        bulk.insert(dict(account))
    return bulk.execute()

def assign_account():
    """
    Returns a tuple of (login_str, path_to_account_form).
    """
    free = account_coll.find_and_modify(
            {'assigned': False},
            {'$set': {'assigned': True}},
            new=True)
    if not free:
        raise Exception('Ran out of free account forms!')
    login = free['login']
    logger.debug('Registered account: {0}'.format(login))
    return (login, os.path.join(account_forms_directory,  "%s.pdf" % login))
