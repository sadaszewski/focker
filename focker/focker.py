#
# Copyright (C) Stanislaw Adaszewski, 2020
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#

from argparse import ArgumentParser
import argparse
import yaml
import os
from functools import reduce
# from weir import zfs, process
from .image import command_image_build, \
    command_image_tag, \
    command_image_untag, \
    command_image_list, \
    command_image_prune, \
    command_image_remove
from .volume import command_volume_create, \
    command_volume_prune, \
    command_volume_list, \
    command_volume_tag, \
    command_volume_untag
import sys
from .zfs import zfs_init
from .jail import command_jail_create, \
    command_jail_start, \
    command_jail_stop, \
    command_jail_remove, \
    command_jail_exec, \
    command_jail_oneshot, \
    command_jail_list, \
    command_jail_tag, \
    command_jail_untag, \
    command_jail_prune
from .compose import \
    command_compose_build, \
    command_compose_run
from .bootstrap import command_bootstrap


class ListForwarderFunctor(object):
    def __init__(self, lst):
        self.lst = lst

    def __call__(self, *args, **kwargs):
        res = []
        for elem in self.lst:
            res.append(elem(*args, **kwargs))
        return ListForwarder(res)


class ListForwarder(object):
    def __init__(self, lst):
        self.lst = lst

    def __getattr__(self, name):
        return ListForwarderFunctor(list(map(lambda a: getattr(a, name), self.lst)))

    def __setattr__(self, name, value):
        if name == 'lst':
            super().__setattr__(name, value)
            return
        # print('setattr(), name:', name, 'value:', value)
        for elem in self.lst:
            setattr(elem, name, value)


def create_parser():
    parser_top = ArgumentParser()
    subparsers_top = parser_top.add_subparsers(dest='L1_command')
    subparsers_top.required = True

    parser = ListForwarder([subparsers_top.add_parser(cmd) for cmd in ['bootstrap', 'boot', 'bs']])
    parser.set_defaults(func=command_bootstrap)

    # image
    subparsers = ListForwarder([ subparsers_top.add_parser(cmd).add_subparsers(dest='L2_command') \
        for cmd in ['image', 'ima', 'img', 'im', 'i'] ])
    subparsers.required = True
    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['build', 'bld', 'b']])
    parser.set_defaults(func=command_image_build)
    parser.add_argument('focker_dir', type=str)
    parser.add_argument('--tags', '-t', type=str, nargs='+', default=[])

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['tag', 't']])
    parser.set_defaults(func=command_image_tag)
    parser.add_argument('reference', type=str)
    parser.add_argument('tags', type=str, nargs='+')

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['untag', 'u']])
    parser.set_defaults(func=command_image_untag)
    parser.add_argument('tags', type=str, nargs='+', default=[])

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['list', 'ls', 'l']])
    parser.set_defaults(func=command_image_list)
    parser.add_argument('--full-sha256', '-f', action='store_true')

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['prune', 'pru', 'p']])
    parser.set_defaults(func=command_image_prune)

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['remove', 'rem', 'rm', 'r']])
    parser.set_defaults(func=command_image_remove)
    parser.add_argument('reference', type=str)
    # parser.add_argument('--remove-children', '-r', action='store_true')
    parser.add_argument('--remove-dependents', '-R', action='store_true')

    # jail
    subparsers = ListForwarder([ subparsers_top.add_parser(cmd).add_subparsers(dest='L2_command') \
        for cmd in ['jail', 'j'] ])
    subparsers.required = True
    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['create', 'creat', 'cre', 'c']])
    parser.set_defaults(func=command_jail_create)
    parser.add_argument('image', type=str)
    parser.add_argument('--command', '-c', type=str, default='/bin/sh')
    parser.add_argument('--tags', '-t', type=str, nargs='+', default=[])
    parser.add_argument('--env', '-e', type=str, nargs='+', default=[])
    parser.add_argument('--mounts', '-m', type=str, nargs='+', default=[])
    parser.add_argument('--hostname', '-n', type=str)

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['start', 'sta', 's']])
    parser.set_defaults(func=command_jail_start)
    parser.add_argument('reference', type=str)

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['stop', 'sto', 'S']])
    parser.set_defaults(func=command_jail_stop)
    parser.add_argument('reference', type=str)

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['remove', 'rem', 'rm', 'r']])
    parser.set_defaults(func=command_jail_remove)
    parser.add_argument('reference', type=str)

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['exec', 'exe', 'e']])
    parser.set_defaults(func=command_jail_exec)
    parser.add_argument('reference', type=str)
    parser.add_argument('command', type=str, nargs=argparse.REMAINDER, default=['/bin/sh'])

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['oneshot', 'one', 'o']])
    parser.set_defaults(func=command_jail_oneshot)
    parser.add_argument('image', type=str)
    parser.add_argument('--env', '-e', type=str, nargs='+', default=[])
    parser.add_argument('--mounts', '-m', type=str, nargs='+', default=[])
    parser.add_argument('command', type=str, nargs=argparse.REMAINDER, default=['/bin/sh'])

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['list', 'ls', 'l']])
    parser.set_defaults(func=command_jail_list)
    parser.add_argument('--full-sha256', '-f', action='store_true')

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['tag', 't']])
    parser.set_defaults(func=command_jail_tag)
    parser.add_argument('reference', type=str)
    parser.add_argument('tags', type=str, nargs='+')

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['untag', 'u']])
    parser.set_defaults(func=command_jail_untag)
    parser.add_argument('tags', type=str, nargs='+')

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['prune', 'pru', 'p']])
    parser.set_defaults(func=command_jail_prune)
    parser.add_argument('--force', '-f', action='store_true')

    # volume
    subparsers = ListForwarder([ subparsers_top.add_parser(cmd).add_subparsers(dest='L2_command') \
        for cmd in ['volume', 'vol', 'v'] ])
    subparsers.required = True
    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['create', 'creat', 'cre', 'c']])
    parser.set_defaults(func=command_volume_create)
    parser.add_argument('--tags', '-t', type=str, nargs='+', default=[])

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['prune', 'pru', 'p']])
    parser.set_defaults(func=command_volume_prune)

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['list', 'ls', 'l']])
    parser.set_defaults(func=command_volume_list)
    parser.add_argument('--full-sha256', '-f', action='store_true')

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['tag', 't']])
    parser.set_defaults(func=command_volume_tag)
    parser.add_argument('reference', type=str)
    parser.add_argument('tags', type=str, nargs='+')

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['untag', 'u']])
    parser.set_defaults(func=command_volume_untag)
    parser.add_argument('tags', type=str, nargs='+')

    # compose
    subparsers = ListForwarder([ subparsers_top.add_parser(cmd).add_subparsers(dest='L2_command') \
        for cmd in ['compose', 'comp', 'c'] ])
    subparsers.required = True
    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['build', 'bld', 'b']])
    parser.set_defaults(func=command_compose_build)
    parser.add_argument('filename', type=str)

    parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['run', 'r']])
    parser.set_defaults(func=command_compose_run)
    parser.add_argument('filename', type=str)
    parser.add_argument('command', type=str)

    return parser_top


def main():
    zfs_init()
    parser = create_parser()
    args = parser.parse_args()
    if not hasattr(args, 'func'):
        parser.print_usage()
        sys.exit('You must choose a mode')

    args.func(args)


if __name__ == '__main__':
    main()
