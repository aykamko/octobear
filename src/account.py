import string
import re
import logging
from db.schema import connection, Account
from . import config

logger = logging.getLogger('Account')
account_coll = connection[config['course_name']][Account.__collection__]

def _register_num_accounts(num):
    def generate_account_list(num):
        accounts = []
        alph = string.lowercase
        i = 0
        for j, c1 in enumerate(' ' + alph):
            # accounts tX and iX are reserved
            c2chars = re.sub(r'[it]', '', alph) if j == 0 else alph
            for c2 in c2chars:
                for c3 in alph:
                    if i >= num:
                        return accounts
                    accounts.append(str(c1 + c2 + c3).strip())
                    i += 1

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

