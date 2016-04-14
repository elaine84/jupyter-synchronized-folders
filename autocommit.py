#!/usr/bin/python3
"""
Simple script that autocommits files being worked on to git.
"""
import time
import argparse
import logging
import tornado
from tornado.gen import Task, coroutine, Return
import tornado.process


@coroutine
def call_subprocess(cmd, stdin=None):
    """
    Wrapper around subprocess call using Tornado's Subprocess class.
    """
    stdin = tornado.process.Subprocess.STREAM

    sub_process = tornado.process.Subprocess(
        cmd,
        stdout=tornado.process.Subprocess.STREAM,
        stderr=tornado.process.Subprocess.STREAM
    )

#    if stdin:
#        yield Task(sub_process.stdin.write, stdin)

#    if stdin:
#        sub_process.stdin.close()

    error = Task(sub_process.stderr.read_until_close)

    yield sub_process.stdout.read_until_close()


@coroutine
def run_git_command(*command):
    logging.info(' '.join([str(c) for c in command]))
    return call_subprocess([
        '/usr/bin/git',
    ] + list(command))

@coroutine
def get_remote_branch_sha(remote, branch):
    remote_head = yield run_git_command(
        'ls-remote',
        '--heads',
        remote, 'refs/heads/{head}'.format(head=branch)
    )
    ipdb.set_trace()
    raise Return(remote_head.split()[0])


@coroutine
def do_rebase_pull(remote='origin', branch='master'):
    yield run_git_command(
        'pull',
        '--rebase',
        '--strategy', 'recursive',
    #    '--strategy-option', 'ours',
        remote, branch
    )


@coroutine
def get_local_sha(branch):
    local_head = yield run_git_command(
        'show-ref',
        'refs/heads/{branch}'.format(branch=branch)
    )
    raise Return(local_head.split()[0])


@coroutine
def sync():
    # git --short produces no output if there has been nothing to commit
    if (yield run_git_command('status', '--short')):
        changed = True
    else:
        changed = False

    if changed:
        # the --all also git rms the files that have been removed
        yield run_git_command('add', '--all', '.')
        try:
            yield run_git_command('commit', '--message', 'Autocommit')
            yield run_git_command('show')
        except Exception:
            logging.exception('error')
            return

    # Find the SHA of the remote master
    remote_head_sha = yield get_remote_branch_sha('origin', 'master')

    # if the local and remote HEADs are same, do not do anything! Both
    # the things are in sync!
    if remote_head_sha != get_local_sha('master'):
        try:
            yield run_git_command(
                'merge-base',
                '--is-ancestor',
                get_local_sha('master'),
                remote_head_sha
            )
            needs_pull = False
        except Exception:
            needs_pull = True

        if needs_pull:
            try:
                yield do_rebase_pull('origin', 'master')
                yield run_git_command(
                    'show'
                )
            except Exception:
                logging.exception('error')
                return

        if remote_head_sha != get_local_sha('master'):
            try:
                yield run_git_command('push', 'origin', 'master')
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
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_callback(sync)
    ioloop.start()
