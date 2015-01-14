import string
import re
import logging
import itertools
from db.schema import connection, Account
from . import config

logger = logging.getLogger('Account')
account_coll = connection[config['course_name']][Account.__collection__]

def generate_account_list(num, minimum_length=2):
    accounts = []
    alph = string.lowercase
    non_reserved = lambda account: account[0] not in ('t', 'r')
    for length in itertools.count(minimum_length):
        accounts.extend(map(''.join, filter(non_reserved, itertools.product(alph, repeat=length))))
        if len(accounts) >= num:
            return accounts[:num]

def _register_num_accounts(num):

    bulk = account_coll.initialize_ordered_bulk_op()
    for account_str in generate_account_list(num):
        account = connection.Account()
        account['account'] = account_str
        bulk.insert(dict(account))
    return bulk.execute()

def register_accounts():
    size = int(config['class_size'])
    return _register_num_accounts(size)

def assign_account():
    free = account_coll.find_and_modify(
            {'assigned': False},
            {'$set': {'assigned': True}},
            new=True)
    logger.debug('Registered account: {0}'.format(free['account']))
    return free['account']

