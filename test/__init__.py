# add root folder to Python path for entire package at runtime
import sys
sys.path.insert(0, '..')

# point all operations to test database
from src import config
testdb = config['course_name'] = 'test-' + config['course_name']

import logging
logging.basicConfig(format='%(name)s: %(message)s')
