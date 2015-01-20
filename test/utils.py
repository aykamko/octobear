import random
import uuid
import logging
import re
import subprocess
import os
import signal
import logging
from inspect import stack

from src import config
testdb = config['course_name']

from src.db.schema import *
from src.account import generate_account_list

from rq import Connection, Worker
from rq.worker import logger as rq_logger
from . import log_level
rq_logger.setLevel(log_level)

class TestUtils:

    def __init__(self, conn=None, logger_name=None, **kwargs):
        if conn:
            self.conn = conn
        else:
            self.conn = connection
        if not logger_name:
            caller_frame = stack()[1]
            path = caller_frame[0].f_globals.get('__file__', None)
            logger_name = re.search(r'/([a-zA-Z0-9_\-\.]*?).py', path).group(1)
        self.logger = logging.getLogger(logger_name)
        self.queue_worker = None

    def start_tests(self, queue_worker=False):
        self.conn.drop_database(testdb)
        self.logger.info('Starting test.')

    def end_tests(self):
        self.conn.drop_database(testdb)
        self.logger.info('Test complete! No other output indicates success.')

    def start_rq_worker(self, queue, burst=True):
        with Connection():
            worker = Worker([queue])
            worker.work(burst=True)

    def generate_students(self, num, bulk=False):
        students = []
        logins = generate_account_list(num)
        students_coll = self.conn[testdb][Member.__collection__]
        if bulk:
            bulk_op = students_coll.initialize_unordered_bulk_op()
        for i in xrange(num):
            s = self.conn.Member()
            s['sid'] = random.randint(10000000, 99999999)
            s['login'] = logins[i]
            s['name'] = 'student-' + str(uuid.uuid4().get_hex())
            if bulk:
                s['grades'] = list(s['grades']) # can't encode set
                bulk.insert(dict(s))
            else:
                s.save()
            students.append(s)
        if bulk:
            bulk.execute()
        assert (self.conn[testdb].command('collstats', Member.__collection__)['count'] == num)
        return students

    def generate_groups(self, num, students, students_per_group, bulk=False):
        groups = []
        groups_coll = self.conn[testdb][Group.__collection__]
        if bulk:
            bulk_op = groups_coll.initialize_unordered_bulk_op()
        end = False
        for i in xrange(num):
            g = self.conn.Group()
            g['name'] = 'group-' + str(uuid.uuid4().get_hex())
            start_idx = i * students_per_group
            for j in range(start_idx, start_idx + students_per_group):
                try:
                    s = students[j]
                except IndexError:
                    end = True
                    break
                s.reload() # reload to get student ID (in case of bulk insert)
                g['members'].add(s['_id'])
            if bulk:
                g['members'] = list(g['members']) # can't encode set
                g['grades'] = list(g['grades'])
                bulk.insert(dict(g))
            else:
                g.save()
            groups.append(g)
            if end:
                break
        if bulk:
            bulk.execute()
        assert (self.conn[testdb].command('collstats', Group.__collection__)['count'] == num)
        return groups

    def generate_assignments(self, num, bulk=False):
        assignments = []
        assignments_coll = self.conn[testdb][Assignment.__collection__]
        if bulk:
            bulk_op = assignments_coll.initialize_unordered_bulk_op()
        for i in xrange(num):
            a = self.conn.Assignment()
            a['name'] = 'hw-' + str(uuid.uuid4().get_hex())
            a['max_score'] = float(random.randint(5, 50))
            if bulk:
                bulk.insert(dict(a))
            else:
                a.save()
            assignments.append(a)
        if bulk:
            bulk.execute()
        assert (self.conn[testdb].command('collstats', Assignment.__collection__)['count'] == num)
        return assignments
