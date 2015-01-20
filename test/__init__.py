# add root folder to Python path for entire package at runtime
import sys
sys.path.insert(0, '..')

# point all operations to test database
from src import config
testdb = config['course_name'] = 'test-' + config['course_name']

import logging
log_level = logging.WARN
logging.basicConfig(
        level=log_level,
        format='%(name)s: %(message)s')
