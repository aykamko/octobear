import argparse
import csv
import getpass
import os
import re
import sys
import urllib
import urllib2

def generate_gradesheet(assignment):


def downloadCSV(key, gid):
    email = GMAIL
    password = GPASS
    client = Client(email, password)
    return client.download(key, gid)

def downloadRoster(assignment, filename, comments, wipe):
    csv_file = downloadCSV(KEY, GID)
    reader = csv.DictReader(csv_file)
    msg = 'ERROR: {} is not a column on the spreadsheet.'
    if assignment not in reader.fieldnames:
        print msg.format(assignment)
        sys.exit(-1)
    if comments and comments not in reader.fieldnames:
        print msg.format(comments)
        sys.exit(-1)
    with open(filename, 'w') as f:
        for row in reader:
            grade = row[assignment].strip() or '---'
            grade = '---' if wipe else grade
            namez = row['Student Name'].replace (" ", "_")
            entry = 'cs162-{} {} {} '.format(
                    row['Login'], namez, grade)
            if comments:
                entry += '{}'.format(row[comments])
            f.write('{}\n'.format(entry))

def uploadGrades(assignment, comments, force, wipe, all):
    if (all):
        filez = open('assign', 'rU')
        for assignment in filez.readlines():
            assignment = assignment[:-1]
            filename = '{}.grades'.format(assignment)
            print filename
            downloadRoster(assignment, filename, comments, wipe)
            f = 'yes | ' if force else ''
            cmd = '{}enter-grades -f {} {}'.format(f, filename, assignment)
            print cmd
            os.system(cmd)
            #os.system('rm {}'.format(filename))
        filez.close()
    else:
        filename = '{}.grades'.format(assignment)
        downloadRoster(assignment, filename, comments, wipe)
        f = 'yes | ' if force else ''
        cmd = '{}enter-grades -f {} {}'.format(f, filename, assignment)
        os.system(cmd)
        #os.system('rm {}'.format(filename))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('assignment',
                        help='Name of Assignment in octobear.')
    args = parser.parse_args()
    uploadGrades(args['assignment'], args['comments'], args['force'], args['wipe'], args['all'])

