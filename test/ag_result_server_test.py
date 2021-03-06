num_students = 6
num_groups = 2 # num_students should be divisible by num_groups
students_per_group = (num_students / num_groups)
num_assignments = 4
num_solo_assignments = (num_assignments / 2)
num_group_assignments = (num_assignments - num_solo_assignments)

import random
import logging
import requests; logging.getLogger('requests').setLevel(logging.WARNING)
import json
import uuid
import time

from utils import TestUtils
util = TestUtils()

from src.ag_result_server import run_ag_result_server, logger, work_queue
logger.setLevel(logging.WARNING)
server = run_ag_result_server('', 0)

from src.db.schema import *

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

"""
POST autograder results (sequentially)
"""
def post_grade(data):
    h = { 'content-type': 'application/json' }
    addr = 'http://localhost:%d' % (server.server_address[1])
    res = requests.post(addr, data=data, headers=h)
    if not res.ok:
        logger.error('Failed request! Status code: {0}\n{1}'.format(
            res.status_code,
            res.content))

for packet in data_packets:
    post_grade(packet)

"""
Handle results in work queue
"""
time.sleep(3)
util.start_rq_worker(work_queue)

"""
Check for successful entry
"""
for a in solo_assignments:
    for s in students:
        query = {'assignment': a['_id'], 'owner': s['_id']}
        grade = connection.Grade.find_one(query);
        if not grade:
            logger.error('Missing grade! {0} {1}'.format(
                a['name'], s['name']))

for a in group_assignments:
    for group in groups:
        query = {'assignment': a['_id'], 'owner': group['_id']}
        grade = connection.Grade.find_one(query);
        if not grade:
            logger.error('Missing grade! {0} {1}'.format(
                a['name'], group['name']))

server.shutdown()

###############################################################################
util.end_tests()
###############################################################################
