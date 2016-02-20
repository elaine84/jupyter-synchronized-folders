#!/usr/bin/python3
"""
Simple script that autocommits files being worked on to git.
"""
import subprocess
import time
import argparse


def run_git_command(*command):
    return subprocess.check_output([
        '/usr/bin/git',
    ] + list(command))


def get_remote_branch_sha(remote, branch):
    remote_head = run_git_command(
        'ls-remote',
        '--heads',
        remote, 'refs/heads/{head}'.format(head=branch)
    )
    remote_head_sha = remote_head.split()[0]

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        'time',
        help='Number of seconds to wait between autocommits'
    )
    args = argparser.parse_args()

    run_git_command(
        'commit',
        '--allow-empty',
        '-m',
        'Starting autocommit with period %s seconds' % args.time
    )

    while True:
        # git --short produces no output if there has been nothing to commit
        if run_git_command('status', '--short'):
            changed = True
        else:
            changed = False

        if changed:
            # the --all also git rms the files that have been removed
            run_git_command('add', '--all', '.')
            try:
                run_git_command('commit', '--message', 'Autocommit')
            except Exception:
                continue

        # Find the SHA of the remote master
        remote_head_sha = get_remote_branch_sha('origin', 'master')

        local_head = run_git_command('show-ref', 'refs/heads/master')
        local_head_sha = local_head.split()[0]

        # if the local and remote HEADs are same, do not do anything! Both
        # the things are in sync!
        if remote_head_sha != local_head_sha:
            try:
                run_git_command(
                    'merge-base',
                    '--is-ancestor',
                    local_head_sha,
                    remote_head_sha
                )
                needs_pull = False
            except subprocess.CalledProcessError:
                needs_pull = True

            if needs_pull:
                try:
                    run_git_command(
                        'pull',
                        '--rebase',
                        '--strategy', 'recursive',
                        '--strategy-option', 'ours',
                        'origin', 'master'
                    )
                except Exception:
                    continue

            if changed:
                try:
                    run_git_command('push', 'origin', 'master')
                except Exception:
                    continue
        time.sleep(float(args.time))
