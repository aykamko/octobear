import csv
import re
from db.schema import connection, Member
from . import config

def parse_enroll(roster_path):
    # TODO: validate file format
    with open(roster_path, 'r') as csvfile:
        roster = csv.reader(csvfile)
        members_coll = connection[config['course_name']][Member.__collection__]
        headers = roster.next()
        def col_for(colname):
            for i, name in enumerate(headers):
                if name == colname:
                    return i
            return
        for row in roster:
            sid_entry = row[col_for('Student ID')]
            sid = int(re.search(r'\d+', sid_entry).group())
            # inserts new SIDs, preserves existing ones
            new_member = dict(connection.Member())
            new_member['sid'] = sid
            members_coll.update(
                    {'sid': sid, 'registered': False},
                    {'$set':new_member},
                    upsert=True)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
            description='Parse student roster file and enroll into MongoDB.')
    parser.add_argument('roster', type=str, nargs=1,
            help='Roster file to parse.')

    args = parser.parse_args()
    parse_enroll(args.roster[0])
