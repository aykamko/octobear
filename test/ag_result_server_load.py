num_threads = 100 # LOL
num_requests = 500
num_students = 1000
num_assignments = 2
ag_result_server_port = 9011

if __name__ == '__main__':

    import sys
    sys.path.insert(0, '..') # root folder to Python path at runtime

    from src import config
    testdb = config['course_name'] = 'test-' + config['course_name']
    from mongokit import Connection
    connection = Connection()
    try:
        connection.drop_database(testdb)
    except Exception:
        pass

    import random
    import logging
    logging.basicConfig(level=logging.WARNING,
            format='%(name)s: %(message)s')
    import requests
    logging.getLogger('requests').setLevel(logging.WARNING)
    import json
    import uuid
    from multiprocessing import Pool
    from src.account import generate_account_list
    from src.ag_result_server import *
    server = run_ag_result_server('', ag_result_server_port)


    """
    Generate students
    """
    students = []
    logins = generate_account_list(num_students)
    students_coll = connection[testdb][Member.__collection__]
    bulk = students_coll.initialize_unordered_bulk_op()
    for i in xrange(num_students):
        s = connection.Member()
        s['sid'] = random.randint(10000000, 99999999)
        s['login'] = logins[i]
        s['name'] = 'student-' + str(uuid.uuid4().get_hex())
        del s['grades'] # can't encode set
        students.append(s)
        bulk.insert(dict(s))
    bulk.execute();
    print 'Added {0} students'.format(num_students)


    """
    Generate assignments
    """
    assignments = []
    for i in xrange(num_assignments):
        a = connection.Assignment()
        a['name'] = 'hw-' + str(uuid.uuid4().get_hex())
        a['max_score'] = random.randint(5, 15)
        a.save()
        assignments.append(a)
    print 'Added {0} assignments'.format(num_assignments)


    """
    Generate requests
    """
    data_packets = []
    for _ in xrange(num_requests):
        s = random.choice(students)
        a = random.choice(assignments)
        data = json.dumps({
            'score': random.randint(0, a['max_score']),
            'assignment': a['name'],
            'login': s['name'],
            'submit': True
        })
        data_packets.append(data)
    print 'Generated {0} requests'.format(num_requests)



    def enter_grade(data):
        h = { 'content-type': 'application/json' }
        addr = 'http://localhost:%d' % (server.server_address[1])
        res = requests.post(addr, data=data, headers=h)
        if not res.ok:
            print 'Failed request!'
            print res.status_code
            print res.content

    print 'Starting thread pool...'
    pool = Pool(num_threads)
    pool.map(enter_grade, data_packets)
    print 'Thread pool done.'

    server.shutdown()
    connection.drop_database(testdb)
