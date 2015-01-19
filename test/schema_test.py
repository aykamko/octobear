num_students = 6
num_groups = 2 # num_students should be divisible by num_groups
students_per_group = (num_students / num_groups)
num_assignments = 4
num_solo_assignments = (num_assignments / 2)
num_group_assignments = (num_assignments - num_solo_assignments)

from src.db.schema import *
from utils import TestUtils
util = TestUtils()

import random

###############################################################################
util.start_tests()
###############################################################################

logger = util.logger

students = util.generate_students(num_students)
groups = util.generate_groups(num_groups, students, students_per_group)
assignments = util.generate_assignments(num_assignments)

solo_assignments = assignments[:num_solo_assignments]
group_assignments = assignments[num_solo_assignments:]

"""
Solo grade tests
"""
for a in solo_assignments:
    for s in students:
        g = connection.Grade()
        g['assignment'] = a['_id']
        g['owner'] = s['_id']
        g['score'] = float(random.randint(0, a['max_score']))
        g.save()

        # check that student contains reference to grade after save
        s.reload()
        if g['_id'] not in s['grades']:
            logger.error('Student does not contain reference to new solo grade!')

"""
Group grade tests
"""
for a in group_assignments:
    for group in groups:
        grade = connection.Grade()
        grade['assignment'] = a['_id']
        grade['owner'] = group['_id']
        grade['group'] = True
        grade['score'] = float(random.randint(0, a['max_score']))
        grade.save()

        # check that group and all group students contain reference to grade after save
        group.reload()
        if grade['_id'] not in group['grades']:
            logger.error('Group does not contain reference to new group grade!')

        for s_id in group['members']:
            s = connection.Member.find_one({'_id': s_id})
            if grade['_id'] not in s['grades']:
                logger.error('Student does not contain reference to new group grade!')

###############################################################################
util.end_tests()
###############################################################################
