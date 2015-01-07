# TODO: make this callable from command line with arguments
import signal
import sys
import time
from .registration_server import run_registration_handler

def run():
    run_registration_handler()

    def SIGINT_handler(signal, frame):
        print '\rExiting...'
        sys.exit(0)

    signal.signal(signal.SIGINT, SIGINT_handler)
    # Wait for interrupt, since signal.pause() isn't on Windows
    while True:
        time.sleep(60)
