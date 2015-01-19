import BaseHTTPServer
import SocketServer
import cgi
import json
import threading
import logging
logger = logging.getLogger('ag_result_server');

from . import config

from db.schema import connection as conn, Assignment, Member, Grade
import emailer


from redis import Redis
from rq import Queue


work_queue = Queue(connection=Redis())
grade_coll = conn[config['course_name']][Grade.__collection__]
def handle_result(data):
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
        logger.error(
                'Received invalid data; required fields are missing.\n{0}'.format(
                jprint.pformat(data)));
        return

    assignment = conn.Assignment.find_one({'name': assignment_name})
    owner = conn.Group.find_one({'name': repo}) if group_repo \
            else conn.Member.find_one({'login': repo})
    if not owner or not assignment:
        logger.error('Assignment or owner do not exist; ignoring ag result.')
        return

    if submit:
        grader = conn.Member.find_one({'login': grader_login});
        result = grade_coll.update(
                {'assignment': assignment['_id'], 'owner': owner['_id']},
                {'$set': {
                    'group': group_repo,
                    'score': score,
                    'grader': (None if not grader else grader['_id']),
                    'comments': comments}
                    },
                upsert=True
                )
        if 'upserted' in result:
            new_grade = conn.Grade.find_one({'_id': result['upserted']})
            new_grade.save() # re-save grade to set up relations

    if email_content and len(email_content):
        to = []
        if group_repo:
            to.append(owner['email'])
        else:
            to.extend([student['email'] for student in
                conn.Member.find({'_id': {'$in': owner['members']}})])
        subject = '[{0} Autograder] {1} Results'.format(config['course-name'], assignment['name'])
        if email_plain:
            emailer.send_plaintext(to, subject, email_content);
        else:
            emailer.send_markdown(to, subject, email_content);

    if raw_output and len(raw_output):
        logger.info(raw_output)

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
