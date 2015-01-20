num_threads = 10
num_students = 200
num_groups = 50 # num_students should be divisible by num_groups
students_per_group = (num_students / num_groups)
num_assignments = 2
num_solo_assignments = (num_assignments / 2)
num_group_assignments = (num_assignments - num_solo_assignments)

import random
import logging
import requests; logging.getLogger('requests').setLevel(logging.WARNING)
import json
import uuid
import time
from multiprocessing import Pool

from utils import TestUtils
util = TestUtils()

from src.ag_result_server import run_ag_result_server, logger, work_queue
from . import log_level
logger.setLevel(log_level)
server = run_ag_result_server('', 0)

from src.db.schema import *
from src import jprint

###############################################################################
util.start_tests()
###############################################################################

logger = util.logger

students = util.generate_students(num_students)
groups = util.generate_groups(num_groups, students, students_per_group)
assignments = util.generate_assignments(num_assignments)

solo_assignments = assignments[:num_solo_assignments]
group_assignments = assignments[num_solo_assignments:]

data_packets = []
check_queries = []

"""
Solo grade tests
"""
for a in solo_assignments:
    for s in students:
        data = json.dumps({
            'score': float(random.randint(0, a['max_score'])),
            'assignment': a['name'],
            'repo': s['login'],
            'submit': True
        })
        data_packets.append(data)
        check_queries.append(({'assignment': a['_id'], 'owner': s['_id']},
            (a, s)))

"""
Group grade tests
"""
for a in group_assignments:
    for group in groups:
        data = json.dumps({
            'score': float(random.randint(0, a['max_score'])),
            'assignment': a['name'],
            'repo': group['name'],
            'group_repo': True,
            'submit': True
        })
        data_packets.append(data)
        check_queries.append(({'assignment': a['_id'], 'owner': group['_id']},
            (a, group)))

"""
POST autograder results (in parallel, load testing)
"""
def post_grade(data):
    h = { 'content-type': 'application/json' }
    addr = 'http://localhost:%d' % (server.server_address[1])
    res = requests.post(addr, data=data, headers=h)
    if not res.ok:
        logger.error('Failed request! Status code: {0}\n{1}'.format(
            res.status_code,
            res.content))

logger.warn('Starting load test thread pool...')
pool = Pool(num_threads)
pool.map_async(post_grade, data_packets)

"""
Handle results in work queue
"""
time.sleep(5)
logger.warn('Starting rq worker...')
util.start_rq_worker(work_queue)

"""
Check for successful entry
"""
logger.warn('Checking entries...')
for cq in check_queries:
    grade = connection.Grade.find_one(cq[0]);
    if not grade:
        logger.error('Missing grade!\n{0}'.format(jprint.pformat(cq[1])))

server.shutdown()

###############################################################################
util.end_tests()
###############################################################################
