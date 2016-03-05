#!/usr/bin/python3
"""
Simple script that autocommits files being worked on to git.
"""
import subprocess
import time
import argparse
import logging
import tornado


def run_git_command(*command):
    logging.info(' '.join([str(c) for c in command]))
    return subprocess.check_output([
        '/usr/bin/git',
    ] + list(command))


def get_remote_branch_sha(remote, branch):
    remote_head = run_git_command(
        'ls-remote',
        '--heads',
        remote, 'refs/heads/{head}'.format(head=branch)
    )
    return remote_head.split()[0]


def do_rebase_pull(remote='origin', branch='master'):
    run_git_command(
        'pull',
        '--rebase',
        '--strategy', 'recursive',
        '--strategy-option', 'ours',
        remote, branch
    )


def get_local_sha(branch):
    local_head = run_git_command(
        'show-ref',
        'refs/heads/{branch}'.format(branch=branch)
    )
    return local_head.split()[0]


def sync():
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
            run_git_command('show')
        except Exception:
            logging.exception('error')
            return

    # Find the SHA of the remote master
    remote_head_sha = get_remote_branch_sha('origin', 'master')

    # if the local and remote HEADs are same, do not do anything! Both
    # the things are in sync!
    if remote_head_sha != get_local_sha('master'):
        try:
            run_git_command(
                'merge-base',
                '--is-ancestor',
                get_local_sha('master'),
                remote_head_sha
            )
            needs_pull = False
        except subprocess.CalledProcessError:
            needs_pull = True

        if needs_pull:
            try:
                do_rebase_pull('origin', 'master')
                run_git_command(
                    'show'
                )
            except Exception:
                logging.exception('error')
                return

        if remote_head_sha != get_local_sha('master'):
            try:
                run_git_command('push', 'origin', 'master')
            except Exception:
                logging.exception('error')
                return


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        'time',
        help='Number of seconds to wait between autocommits'
    )
    args = argparser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(message)s'
    )

    run_git_command(
        'commit',
        '--allow-empty',
        '-m',
        'Starting autocommit with period %s seconds' % args.time
    )

    while True:
        sync()
        time.sleep(float(args.time))
