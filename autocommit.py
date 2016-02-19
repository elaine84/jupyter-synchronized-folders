#!/usr/bin/python3
"""
Simple script that autocommits files being worked on to git.

Test change with Github personal access token (testing swap file
fix after pulling in changes manually).
"""
import subprocess
import time
import argparse



def run_git_command(*command):
    subprocess.check_call([
        '/usr/bin/git',
    ] + list(command))



if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('time', help='Number of seconds to wait between autocommits')
    args = argparser.parse_args()

    run_git_command('commit', '--allow-empty', '-m', 'Starting autocommit with period %s seconds' % args.time)

    while True:
        run_git_command('add', '--all', '.')
        try:
            run_git_command('commit', '-m', 'Autocommit')
        except:
            pass

        run_git_command('pull', '-r', '-s', 'recursive', '-Xours', 'origin', 'master')

        try:
            run_git_command('push', 'origin', 'master')
        except:
            continue
        time.sleep(float(args.time))
