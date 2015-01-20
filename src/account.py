import string
import re
import logging
import itertools
import os
from PyPDF2 import PdfFileWriter, PdfFileReader
from db.schema import connection, Account
from . import config

logger = logging.getLogger('Account')
account_coll = connection[config['course_name']][Account.__collection__]
split_accounts_dir = os.path.dirname(__file__) + '/account_forms'

def split_store_account_forms(account_forms, minimum_length=2):
    bulk_acct_pdfs = [PdfFileReader(open(form, "rb")) for form in account_forms]
    try:
        os.mkdir(split_accounts_dir)
    except OSError:
        pass
    num_accounts = sum(bulk.getNumPages() for bulk in bulk_acct_pdfs)
    logins = generate_login_list(num_accounts, minimum_length)
    logger.warn('Generating {0} account forms.'.format(len(logins)))

    # TODO: hacky don't care will fix later
    login_idx = 0
    for i, bulk in enumerate(bulk_acct_pdfs):
        logger.warn('Splitting pdf {0}: {1}'.format(i + 1, os.path.basename(account_forms[i])))
        for j in xrange(bulk.getNumPages()):
            output = PdfFileWriter()
            output.addPage(bulk.getPage(j))
            split_name = split_accounts_dir + ('/%s' % logins[login_idx]) + ".pdf"
            login_idx += 1
            with open(split_name, "wb") as output_stream:
                output.write(output_stream)
    return num_accounts

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
    return (login, split_accounts_dir + ('/%s.pdf' % (login)))
