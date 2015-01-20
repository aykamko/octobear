import BaseHTTPServer
import SocketServer
import cgi
import json
import threading
import logging
logger = logging.getLogger('ag_result_server');

from . import config, jprint

from db.schema import connection as conn, Assignment, Member, Grade
import emailer

from redis import Redis
from rq import Queue
work_queue = Queue(connection=Redis())

class AutograderResultException(Exception):
    pass

def handle_result(data):
    """
    Handles output from an autograder.
    This function has the ability to record a score in the database, email
    students their results, and log the raw output from the autograder.
    """
    try:
        # required
        score           = float(data['score'])
        assignment_name = data['assignment']
        repo            = data['repo']
        submit          = bool(data['submit'])
        # optional
        group_repo      = bool(data.get('group_repo'))
        grader_login    = data.get('grader_login')
        comments        = data.get('comments')
        email_content   = data.get('email_content')
        email_plain     = bool(data.get('email_plain'))
        raw_output      = data.get('raw_output')
    except KeyError:
        raise AutograderResultException(
                'Received invalid data; required fields are missing.\n{0}'.format(
                jprint.pformat(data)));

    assignment = conn.Assignment.find_one({'name': assignment_name})
    owner = conn.Group.find_one({'name': repo}) if group_repo \
            else conn.Member.find_one({'login': repo})
    if not owner or not assignment:
        raise AutograderResultException(
                'Assignment or owner do not exist; ignoring ag result.\n{0}.'.format(
                jprint.pformat(data)))

    if submit:
        submit_grade(assignment['_id'], owner['_id'], group_repo, score,
                grader_login=grader_login, comments=comments)

    if email_content:
        recipients = []
        if group_repo:
            recipients.append(owner['email'])
        else:
            recipients.extend([student['email'] for student in
                conn.Member.find({'_id': {'$in': owner['members']}})])
        email_results(recipients, assignment['name'], email_content)

    if raw_output:
        logger.info(raw_output)

def submit_grade(assignment_id, owner_id, group_repo, score,
        grader_login=None, comments=None):
    """
    Submits grade into database.
    """
    grader = conn.Member.find_one({'login': grader_login}) if grader_login \
            else None
    result = grade_coll.update(
            {'assignment': assignment_id, 'owner': owner_id},
            {'$set': {
                'group': group_repo,
                'score': score,
                'grader': (grader['_id'] if grader else None),
                'comments': comments}
                },
            upsert=True
            )
    if 'upserted' in result:
        new_grade = conn.Grade.find_one({'_id': result['upserted']})
        new_grade.save() # re-save grade to set up relations

grade_coll = conn[config['course_name']][Grade.__collection__]
def email_results(recipients, assignment_name, email_content):
    """
    Emails autograder output to recipient students.
    """
    subject = '[{0} Autograder] {1} Results'.format(config['course-name'], assignment_name)
    if email_plain:
        emailer.send_plaintext(recipients, subject, email_content);
    else:
        emailer.send_markdown(recipients, subject, email_content);


class AutograderResultHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
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
            logger.debug('Recieved autograder result:\n{0}'.format(
                jprint.pformat(data)))
            work_queue.enqueue(handle_result, data)
            self.send_response(200)
        else:
            logger.warn('Content type is not JSON; sending 403.')
            self.send_error(403, 'Content type must be JSON.')

    def log_message(self, format, *args):
        logger.info(format % args)

    def shutdown(self):
        logger.info('Shutting down.')
        super(self.__class__, self).shutdown(self)

def run_ag_result_server(host='', port=int(config['ag_result_server_port'])):
    server_address = (host, port)
    server = SocketServer.TCPServer(server_address, AutograderResultHandler)
    server.request_queue_size = 50 # increase maximum simultaneous requests

    t = threading.Thread(target=server.serve_forever)
    t.setDaemon(True) # don't hang on exit
    t.start()

    logger = logging.getLogger('ag_result_server')
    logger.info('AutograderResultHandler started on {0}'.format(server.server_address))
    return server
