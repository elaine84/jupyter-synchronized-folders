#!/usr/bin/python3
"""
Simple script that autocommits files being worked on to git.
"""
import subprocess
import time
import argparse
from datetime import datetime



def run_git_command(*command):
    subprocess.check_call([
        '/usr/bin/git',
    ] + list(command))



if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('time', help='Number of seconds to wait between autocommits')
    args = argparser.parse_args()

    while True:
        run_git_command('add', '.')
        try:
            run_git_command('commit', '-m', 'Autocommit at %s' % datetime.now())
        except:
            pass
        run_git_command('pull', '-r', '-s', 'recursive', '-Xours', 'origin', 'master')
        run_git_command('push', 'origin', 'master')
        time.sleep(float(args.time))
