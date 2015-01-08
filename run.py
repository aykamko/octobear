#!/usr/bin/env python
import argparse
from src import app, process_roster

parser = argparse.ArgumentParser(
        description='Run deamons for git infrastructure.')
parser.add_argument('--roster',
        dest='roster',
        nargs=1,
        required=False,
        help='Roster file to parse.')

args = parser.parse_args()

if args.roster:
    roster_file = args.roster[0]
    print 'Enrolling from roster file: {0}'.format(roster_file)
    process_roster.parse_enroll(roster_file)

app.run()
