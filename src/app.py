import signal
import sys
import time
from . import config
from .registration_server import run_registration_server
from .ag_result_server import run_ag_result_server
<<<<<<< HEAD
from .queue_worker import start as start_queue_worker

def run():
    rserver = run_registration_server(port=int(config['registration_server_port']))
    agserver = run_ag_result_server(port=int(config['ag_result_server_port']))
    start_queue_worker()
=======

def run():
    run_registration_server(port=int(config['registration_server_port']))
    run_ag_result_server(port=int(config['ag_result_server_port']))
>>>>>>> 5458c59cde41b45fa6fbe494a335524d25c164d8

    def SIGINT_handler(signal, frame):
        print '\rExiting...'
        rserver.shutdown();
        agserver.shutdown();
        sys.exit(0)

    signal.signal(signal.SIGINT, SIGINT_handler)
    # Wait for interrupt, since signal.pause() isn't on Windows
    while True:
        time.sleep(60)
