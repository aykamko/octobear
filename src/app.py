# TODO: make this callable from command line with arguments
import signal
import sys
from .registration_server import run_registration_handler

def run():
    run_registration_handler()

    def SIGINT_handler(signal, frame):
        print '\rExiting...'
        sys.exit(0)

    signal.signal(signal.SIGINT, SIGINT_handler)
    signal.pause()
