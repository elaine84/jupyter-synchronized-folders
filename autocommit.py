#!/usr/bin/python3
"""
Simple script that autocommits files being worked on to git.
"""
import subprocess
from datetime import datetime


def run_git_command(*command):
    subprocess.check_call([
        '/usr/bin/git',
    ] + list(command))


if __name__ == '__main__':
    run_git_command('add', '.')
    run_git_command('commit', '-m', 'Autocommit at %s' % datetime.now())
    run_git_command('pull', '-r', '-s', 'recursive', '-Xours', 'origin' 'master')
    run_git_command('push', 'origin', 'master')
        git push origin master
