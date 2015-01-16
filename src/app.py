import signal
import sys
import time
from . import config
from .registration_server import run_registration_server
from .ag_result_server import run_ag_result_server

def run():
    run_registration_server(port=int(config['registration_server_port']))
    run_ag_result_server(port=int(config['ag_result_server_port']))

    def SIGINT_handler(signal, frame):
        print '\rExiting...'
        sys.exit(0)

    signal.signal(signal.SIGINT, SIGINT_handler)
    # Wait for interrupt, since signal.pause() isn't on Windows
    while True:
        time.sleep(60)
