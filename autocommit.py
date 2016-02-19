#!/bin/python3
"""
Simple script that autocommits files being worked on to git.
"""
import subprocess


def run_git_command(*command):
    subprocess.check_output([
        '/usr/bin/git',
    ] + command)
