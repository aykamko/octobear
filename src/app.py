import signal
import sys
import time
from . import config
from .registration_server import run_registration_server
from .ag_result_server import run_ag_result_server
from .queue_worker import start as start_queue_worker

def run(no_account_forms=False):
    if no_account_forms:
        config['no_account_forms'] = True
    rserver = run_registration_server(port=int(config['registration_server_port']))
    agserver = run_ag_result_server(port=int(config['ag_result_server_port']))
    start_queue_worker()

    def SIGINT_handler(signal, frame):
        print '\rExiting...'
        rserver.shutdown();
        agserver.shutdown();
        sys.exit(0)

    signal.signal(signal.SIGINT, SIGINT_handler)
    # Wait for interrupt, since signal.pause() isn't on Windows
    while True:
        time.sleep(60)
