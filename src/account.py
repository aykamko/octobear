import string
import re
import logging
import os
from os.path import dirname
from db.schema import connection, Account
from . import config

logger = logging.getLogger('Account')
account_coll = connection[config['course_name']][Account.__collection__]
account_forms_directory = os.path.join(dirname(dirname(__file__)), "account_forms")

def generate_login_list(num, minimum_length=2):
    """Generates a dummy account list (FOR TESTING ONLY)"""
    accounts = []
    alph = string.lowercase
    non_reserved = lambda account: account[0] not in ('t', 'r', 'l') # TRL
    for length in itertools.count(minimum_length):
        accounts.extend(map(''.join, filter(non_reserved, itertools.product(alph, repeat=length))))
        if len(accounts) >= num:
            return accounts[:num]

def register_num_accounts(num, minimum_length=2):
    """Inserts a dummy account list into database (FOR TESTING ONLY)"""
    bulk = account_coll.initialize_ordered_bulk_op()
    for account_str in generate_login_list(num, minimum_length=minimum_length):
        account = connection.Account()
        account['login'] = account_str
        bulk.insert(dict(account))
    return bulk.execute()

def register_logins():
    logins = [file_name[:-len(".pdf")]
            for file_name in os.listdir(account_forms_directory)
            if file_name.endswith(".pdf")]

    # Sanity check
    login_matcher = re.compile(r"^[a-z]{2,3}$")
    for login in logins:
        if login_matcher.search(login) is None:
            raise RuntimeError(
                    "Cowardly refusing to process unrecognized login: %s" % login)

    bulk = account_coll.initialize_ordered_bulk_op()
    for login in logins:
        account = connection.Account()
        account["login"] = login
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
