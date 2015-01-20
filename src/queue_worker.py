#!/usr/bin/env python
from . import config
import sys
from multiprocessing import Process
from rq import Queue, Connection, Worker

from github.github import GitHub

def start():
    # Preload github
    github = GitHub(config['gh_organization'], config['gh_user'], config['gh_pass'])

    def work():
        # Provide queue names to listen to as arguments to this script,
        # similar to rqworker
        with Connection():
            qs = map(Queue, sys.argv[1:]) or [Queue()]
            w = Worker(qs)
            w.work()

    p = Process(target=work)
    p.daemon = True
    p.start()

if __name__ == '__main__':
    start()
