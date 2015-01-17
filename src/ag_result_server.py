import BaseHTTPServer
import SocketServer
import cgi
import json
import threading
import logging

from . import config

from db.schema import connection, Assignment, Member, Grade
import emailer


from redis import Redis
from rq import Queue


work_queue = Queue(connection=Redis())
grade_coll = connection[config['course_name']][Grade.__collection__]
def handle_result(data):
    try:
        # required
        score           = int(data['score'])
        assignment_name = data['assignment']
        student_login   = data['login']
        submit          = bool(data['submit'])
        # optional
        grader_login    = data.get('grader_login')
        comments        = data.get('comments')
        email_content   = data.get('email_content')
        email_plain     = bool(data.get('email_plain'))
        raw_output      = data.get('raw_output')
    except KeyError:
        # TODO: log bad data
        return
    assignment = connection.Assignment.find_one({'name': assignment_name})
    student = connection.Member.find_one({'login': student_login});
    if not assignment or not student:
        # TODO: log error
        return
    if submit:
        grader = connection.Member.find_one({'login': grader_login});
        result = grade_coll.update(
                {'assignment': assignment['_id'], 'student': student['_id']},
                {'$set': {'score': score, 'grader': (None if not grader else grader['_id']), 'comments': comments}},
                upsert=True
                )
        if 'upserted' in result:
            new_grade_id = result['upserted']
            student['grades'].add(new_grade_id)
            student.save()
    if email_content and len(email_content):
        to = student['email']
        subject = '[{0}-ag] {1} Results'.format(config['course-name'], assignment['name'])
        if email_plain:
            emailer.send_plaintext(to, subject, email_content);
        else:
            emailer.send_markdown(to, subject, email_content);
    if raw_output and len(raw_output):
        # TODO: log raw_output somewhere
        pass

class AutograderResultHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('AutograderResultHandler')
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_POST(self):
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        except Exception:
            self.send_error(403, 'No Content-Type in header.')
            return
        if ctype == 'application/json':
            length = int(self.headers.getheader('content-length'))
            data = json.loads(self.rfile.read(length))
            self.logger.debug('Recieved autograder result: {0}'.format(data))
            # TODO: stub for @Vaishaal
            work_queue.enqueue(handle_result,data)
            self.send_response(200)
        else:
            self.logger.debug('Content type is not JSON; sending 403.')
            self.send_error(403, 'Content type must be JSON.')

    def shutdown(self):
        self.logger.debug('Shutting down.')
        super(self.__class__, self).shutdown(self)

def run_ag_result_server(host='', port=int(config['ag_result_server_port'])):
    server_address = (host, port)
    server = SocketServer.TCPServer(server_address, AutograderResultHandler)

    t = threading.Thread(target=server.serve_forever)
    t.setDaemon(True) # don't hang on exit
    t.start()

    logger = logging.getLogger('ag_result_server')
    logger.debug('AutograderResultHandler started on {0}'.format(server.server_address))
    return server
