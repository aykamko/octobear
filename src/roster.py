import csv
import re
from db.schema import connection, Member
from . import config

def parse_enroll(roster_path):
    # TODO: validate file format
    print roster_path
    with open(roster_path, 'r') as roster_file:
        members_coll = connection[config['course_name']][Member.__collection__]
        student_ids = roster_file.readlines()
        for sid in student_ids:
            new_member = connection.Member()
            new_member['sid'] = int(sid.replace("\n",""))
            new_member.save()    

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
            description='Parse student roster file and enroll into MongoDB.')
    parser.add_argument('roster', type=str, nargs=1,
            help='Roster file to parse.')

    args = parser.parse_args()
    parse_enroll(args.roster[0])
