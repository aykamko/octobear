num_students = 6
num_groups = 2 # num_students should be divisible by num_groups
students_per_group = (num_students / num_groups)
num_assignments = 4
num_solo_assignments = (num_assignments / 2)
num_group_assignments = (num_assignments - num_solo_assignments)
ag_result_server_port = 9011

import random
import logging
import requests; logging.getLogger('requests').setLevel(logging.WARNING)
import json
import uuid
from rq import Connection, Worker

from utils import TestUtils
util = TestUtils()

from src.ag_result_server import *
server = run_ag_result_server('', ag_result_server_port)

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

# serve requests
with Connection():
    worker = Worker([work_queue])
    worker.work(burst=True)

server.shutdown()

###############################################################################
util.end_tests()
###############################################################################
