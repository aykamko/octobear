#!/usr/bin/env python
from . import config
import sys
from multiprocessing import Process
from rq import Queue, Connection, Worker


def start():
    # Preload github
    from github.github import GitHub

    def work():
        with Connection():
            w = Worker([Queue()])
            w.work()

    p = Process(target=work)
    p.daemon = True
    p.start()

if __name__ == '__main__':
    start()
