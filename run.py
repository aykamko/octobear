#!/usr/bin/env python
import argparse
from src import app, roster, account

if __name__ == '__main__':
    print 'Starting...'
    parser = argparse.ArgumentParser(
            description='Run deamons for git infrastructure.')
    parser.add_argument('--roster',
            dest='roster',
            nargs=1,
            required=False,
            help='Roster file to parse.')
    parser.add_argument('--init',
            action='store_true',
            required=False,
            help='Initializes database with account forms.')

    args = parser.parse_args()

    if args.roster:
        roster_file = args.roster[0]
        print 'Enrolling from roster file: {0}'.format(roster_file)
        roster.parse_enroll(roster_file)

    if args.init:
        print 'Initializing account forms.'
        print account.register_accounts()

    app.run()
