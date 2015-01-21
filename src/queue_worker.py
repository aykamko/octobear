#!/usr/bin/env python
from . import config, logdir
import logging
import sys
from multiprocessing import Process
from rq import Queue, Connection, Worker
from rq.worker import logger

rqLoggerFileHandler = logging.FileHandler(logdir + "/worker.log")
rqLoggerFileHandler.setFormatter(logging.Formatter(
    fmt='%(asctime)s %(message)s',
    datefmt='%H:%M:%S'))
logger.addHandler(rqLoggerFileHandler)

def start():
    def work():
        with Connection():
            w = Worker([Queue()])
            w.work()

    p = Process(target=work)
    p.daemon = True
    p.start()

if __name__ == '__main__':
    start()
