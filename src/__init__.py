###############################################################################
# Parse config
###############################################################################
import os
import re
ignore_line = re.compile('\s*(#.*|\s*$)')
config_line = re.compile('\s*(\w+)\s*=\s*(.+)')

def parse_config(cfgfile):
    config = {}
    for line_no, line in enumerate(cfgfile.readlines()):
        if bool(ignore_line.match(line)): continue
        try:
            m = config_line.match(line)
            if not m:
                continue
            k, v = m.group(1), m.group(2)
            config[k] = v
        except Exception as e:
            print 'Error: line %d: %s' % (line_no, e)
    return config

config = parse_config(open(os.path.dirname(__file__) + '/config', 'r'))

###############################################################################
# Logging
###############################################################################
import logging
import sys

logdir = config['log_dir']
logfile = logdir + "/octobear.log"
try:
    os.mkdir(logdir)
except OSError:
    pass

rootlogger = logging.getLogger()
rootlogger.setLevel(int(config['log_level']))
logFormatter = logging.Formatter('%(name)s: %(message)s')

fileHandler = logging.FileHandler(logfile)
fileHandler.setFormatter(logFormatter)
rootlogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
rootlogger.addHandler(consoleHandler)

###############################################################################
# PrettyPrinter
###############################################################################
import pprint
jprint = pprint.PrettyPrinter(indent=2, width=1)
