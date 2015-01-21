###############################################################################
#
#   WARNING
#
#   USE WITH CAUTION
#
###############################################################################
from .schema import *
from .. import config

def free_all_accounts():
    accounts_coll = connection[config['course_name']][Account.__collection__]
    accounts_coll.update(
            {'assigned': True},
            {'$set': {'assigned': False}}
            )

def unregister_all_users():
    members_coll = connection[config['course_name']][Member.__collection__]
    members_coll.update(
            {'registered': True},
            {'$set': {'registered': False}}
            )
