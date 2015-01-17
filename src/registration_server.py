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
import emailer

from github.github import GitHub
github = GitHub(config['gh_organization'], config['gh_user'], config['gh_pass'])

class RegistrationException(Exception):
    pass

class RegistrationHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('RegistrationHandler')
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def register_member(self, data):
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
        user[u'account'] = free_account
        user.save()
        # user saved in db, so we can now email him and register his github repo
        emailer.send_template(user[u'email'], '[cs61b] Registered!', 'registered.html', user=user)
        github.createEverything(
                user[u'account'],
                [user[u'github']],
                'http://www.alekskamko.com'
                )

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'application/json':
            length = int(self.headers.getheader('content-length'))
            data = json.loads(self.rfile.read(length))
            self.logger.debug('Recieved registration: {0}'.format(data))
            try:
                self.register_member(data)
            except RegistrationException as e:
                self.send_error(400, e.message)
                return
            self.send_response(200)
        else:
            self.logger.debug('Content type is not JSON; sending 403.')
            self.send_error(403, 'Content type must be JSON.')

def run_registration_server(host='', port=int(config['registration_server_port'])):
    server_address = (host, port)
    server = SocketServer.TCPServer(server_address, RegistrationHandler)

    t = threading.Thread(target=server.serve_forever)
    t.setDaemon(True) # don't hang on exit
    t.start()

    logger = logging.getLogger('registration_server')
    logger.debug('RegistrationHandler started on {0}'.format(server.server_address))
