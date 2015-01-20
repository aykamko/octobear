import BaseHTTPServer
import SocketServer
import cgi
import json
import threading
import logging
import datetime

from . import config

import account

from db.schema import connection

from redis import Redis
from rq import Queue

import emailer

work_queue = Queue(connection=Redis())

class RegistrationException(Exception):
    pass

def register_member(data):
    try:
        sid = int(data['sid'])
        user = connection.Member.find_one({'sid': sid})
        if not user:
            raise RegistrationException('SID %d is not enrolled.' % (sid))
        if user['registered']:
            raise RegistrationException('SID %d is already registered.' % (sid))
        user[u'name'] = data['name']
        user[u'email'] = data['email']
        user[u'github'] = data['github']
        user[u'registered'] = True
        user[u'time_registered'] = datetime.datetime.now()
    except KeyError:
        raise RegistrationException('Invalid data; missing fields.')
    free_account = account.assign_account()
    if free_account == None:
        raise RegistrationException('Ran out of free account forms')

    user[u'login'] = free_account
    user.save()
    # user saved in db, so we can now email him and register his github repo
    emailer.send(user, '[{0}] Registered!'.format(config['course_name']), 'registered.html')
    github.createEverything(
            user[u'login'],
            [user[u'github']],
            config['jenkins_hook']
            )

class RegistrationHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('RegistrationHandler')
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'application/json':
            length = int(self.headers.getheader('content-length'))
            data = json.loads(self.rfile.read(length))
            self.logger.debug('Recieved registration: {0}'.format(data))
            work_queue.enqueue(register_member,data)
            self.send_response(200)
        else:
            self.logger.debug('Content type is not JSON; sending 403.')
            self.send_error(403, 'Content type must be JSON.')

    def shutdown(self):
        self.logger.debug('Shutting down.')
        super(self.__class__, self).shutdown(self)

def run_registration_server(host='', port=int(config['registration_server_port'])):
    server_address = (host, port)
    server = SocketServer.TCPServer(server_address, RegistrationHandler)

    t = threading.Thread(target=server.serve_forever)
    t.setDaemon(True) # don't hang on exit
    t.start()

    logger = logging.getLogger('registration_server')
    logger.debug('RegistrationHandler started on {0}'.format(server.server_address))
    return server
