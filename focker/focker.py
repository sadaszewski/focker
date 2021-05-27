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
    command_volume_untag, \
    command_volume_remove, \
    command_volume_set, \
    command_volume_get, \
    command_volume_protect, \
    command_volume_unprotect
import sys
from .zfs import zfs_init
from .jail import command_jail_create, \
    command_jail_start, \
    command_jail_stop, \
    command_jail_restart, \
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
from .misc import focker_lock
from .plugin import Plugins


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
    parser_dict = {}

    parser_dict['top'] = parser_top = ArgumentParser()
    subparsers_top = parser_top.add_subparsers(dest='L1_command')
    subparsers_top.required = True

    parser_dict['bootstrap'] = parser = ListForwarder([subparsers_top.add_parser(cmd) for cmd in ['bootstrap', 'boot', 'bs']])
    parser.set_defaults(func=command_bootstrap)
    parser.add_argument('--tags', '-t', type=str, nargs='+', default=[])
    parser.add_argument('--no-image', action='store_true')
    parser.add_argument('--empty', '-e', action='store_true')
    parser.add_argument('--unfinalized', '-u', action='store_true')
    parser.add_argument('--non-interactive', '-n', action='store_true')
    parser.add_argument('--create-interface', '-c', action='store_true')
    parser.add_argument('--interface', '-i', type=str, default='lo1')
    parser.add_argument('--rename-interface', '-r', type=str, default=None)
    parser.add_argument('--add-pf-rule', '-a', action='store_true')
    parser.add_argument('--external-interface', '-x', type=str, default=None)
    parser.add_argument('--full-auto', '-f', action='store_true')

    # image
    parser_dict['image'] = subparsers = ListForwarder([ subparsers_top.add_parser(cmd).add_subparsers(dest='L2_command') \
        for cmd in ['image', 'ima', 'img', 'im', 'i'] ])
    subparsers.required = True
    parser_dict['image.build'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['build', 'bld', 'b']])
    parser.set_defaults(func=command_image_build)
    parser.add_argument('focker_dir', type=str)
    parser.add_argument('--tags', '-t', type=str, nargs='+', default=[])
    parser.add_argument('--squeeze', '-s', action='store_true')

    parser_dict['image.tag'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['tag', 't']])
    parser.set_defaults(func=command_image_tag)
    parser.add_argument('reference', type=str)
    parser.add_argument('tags', type=str, nargs='+')

    parser_dict['image.untag'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['untag', 'u']])
    parser.set_defaults(func=command_image_untag)
    parser.add_argument('tags', type=str, nargs='+', default=[])

    parser_dict['image.list'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['list', 'ls', 'l']])
    parser.set_defaults(func=command_image_list)
    parser.add_argument('--full-sha256', '-f', action='store_true')
    parser.add_argument('--tagged-only', '-t', action='store_true')

    parser_dict['image.prune'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['prune', 'pru', 'p']])
    parser.set_defaults(func=command_image_prune)

    parser_dict['image.remove'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['remove', 'rem', 'rm', 'r']])
    parser.set_defaults(func=command_image_remove)
    parser.add_argument('reference', type=str)
    # parser.add_argument('--remove-children', '-r', action='store_true')
    parser.add_argument('--remove-dependents', '-R', action='store_true')
    parser.add_argument('--force', '-f', action='store_true')

    # jail
    parser_dict['jail'] = subparsers = ListForwarder([ subparsers_top.add_parser(cmd).add_subparsers(dest='L2_command') \
        for cmd in ['jail', 'j'] ])
    subparsers.required = True
    parser_dict['jail.create'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['create', 'creat', 'cre', 'c']])
    parser.set_defaults(func=command_jail_create)
    parser.add_argument('image', type=str)
    parser.add_argument('--command', '-c', type=str, default='/bin/sh')
    parser.add_argument('--tags', '-t', type=str, nargs='+', default=[])
    parser.add_argument('--env', '-e', type=str, nargs='+', default=[])
    parser.add_argument('--mounts', '-m', type=str, nargs='+', default=[])
    parser.add_argument('--hostname', '-n', type=str)

    parser_dict['jail.start'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['start', 'sta', 's']])
    parser.set_defaults(func=command_jail_start)
    parser.add_argument('reference', type=str)

    parser_dict['jail.stop'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['stop', 'sto', 'S']])
    parser.set_defaults(func=command_jail_stop)
    parser.add_argument('reference', type=str)

    parser_dict['jail.restart'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['restart', 're', 'R']])
    parser.set_defaults(func=command_jail_restart)
    parser.add_argument('reference', type=str)

    parser_dict['jail.remove'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['remove', 'rem', 'rm', 'r']])
    parser.set_defaults(func=command_jail_remove)
    parser.add_argument('reference', type=str)
    parser.add_argument('--force', '-f', action='store_true')

    parser_dict['jail.exec'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['exec', 'exe', 'e']])
    parser.set_defaults(func=command_jail_exec)
    parser.add_argument('reference', type=str)
    parser.add_argument('command', type=str, nargs=argparse.REMAINDER, default=['/bin/sh'])

    parser_dict['jail.oneshot'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['oneshot', 'one', 'o']])
    parser.set_defaults(func=command_jail_oneshot)
    parser.add_argument('image', type=str)
    parser.add_argument('--env', '-e', type=str, nargs='+', default=[])
    parser.add_argument('--mounts', '-m', type=str, nargs='+', default=[])
    parser.add_argument('command', type=str, nargs=argparse.REMAINDER, default=['/bin/sh'])

    parser_dict['jail.list'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['list', 'ls', 'l']])
    parser.set_defaults(func=command_jail_list)
    parser.add_argument('--full-sha256', '-f', action='store_true')
    parser.add_argument('--images', '-i', action='store_true')

    parser_dict['jail.tag'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['tag', 't']])
    parser.set_defaults(func=command_jail_tag)
    parser.add_argument('reference', type=str)
    parser.add_argument('tags', type=str, nargs='+')

    parser_dict['jail.untag'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['untag', 'u']])
    parser.set_defaults(func=command_jail_untag)
    parser.add_argument('tags', type=str, nargs='+')

    parser_dict['jail.prune'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['prune', 'pru', 'p']])
    parser.set_defaults(func=command_jail_prune)
    parser.add_argument('--force', '-f', action='store_true')

    # volume
    parser_dict['volume'] = subparsers = ListForwarder([ subparsers_top.add_parser(cmd).add_subparsers(dest='L2_command') \
        for cmd in ['volume', 'vol', 'v'] ])
    subparsers.required = True
    parser_dict['volume.create'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['create', 'creat', 'cre', 'c']])
    parser.set_defaults(func=command_volume_create)
    parser.add_argument('--tags', '-t', type=str, nargs='+', default=[])

    parser_dict['volume.prune'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['prune', 'pru', 'p']])
    parser.set_defaults(func=command_volume_prune)

    parser_dict['volume.list'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['list', 'ls', 'l']])
    parser.set_defaults(func=command_volume_list)
    parser.add_argument('--full-sha256', '-f', action='store_true')

    parser_dict['volume.tag'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['tag', 't']])
    parser.set_defaults(func=command_volume_tag)
    parser.add_argument('reference', type=str)
    parser.add_argument('tags', type=str, nargs='+')

    parser_dict['volume.untag'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['untag', 'u']])
    parser.set_defaults(func=command_volume_untag)
    parser.add_argument('tags', type=str, nargs='+')

    parser_dict['volume.remove'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['remove', 'rm', 'r']])
    parser.set_defaults(func=command_volume_remove)
    parser.add_argument('references', type=str, nargs='+')
    parser.add_argument('--force', '-f', action='store_true')

    parser_dict['volume.set'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['set', 's']])
    parser.set_defaults(func=command_volume_set)
    parser.add_argument('reference', type=str)
    parser.add_argument('properties', type=str, nargs=argparse.REMAINDER)

    parser_dict['volume.get'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['get', 'g']])
    parser.set_defaults(func=command_volume_get)
    parser.add_argument('reference', type=str)
    parser.add_argument('properties', type=str, nargs=argparse.REMAINDER)

    parser_dict['volume.protect'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['protect']])
    parser.set_defaults(func=command_volume_protect)
    parser.add_argument('references', type=str, nargs='+')

    parser_dict['volume.unprotect'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['unprotect']])
    parser.set_defaults(func=command_volume_unprotect)
    parser.add_argument('references', type=str, nargs='+')

    # compose
    parser_dict['compose'] = subparsers = ListForwarder([ subparsers_top.add_parser(cmd).add_subparsers(dest='L2_command') \
        for cmd in ['compose', 'comp', 'c'] ])
    subparsers.required = True

    parser_dict['compose.build'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['build', 'bld', 'b']])
    parser.set_defaults(func=command_compose_build)
    parser.add_argument('filename', type=str)
    parser.add_argument('--squeeze', '-s', action='store_true')

    parser_dict['compose.run'] = parser = ListForwarder([subparsers.add_parser(cmd) for cmd in ['run', 'r']])
    parser.set_defaults(func=command_compose_run)
    parser.add_argument('filename', type=str)
    parser.add_argument('command', type=str)

    return parser_top, parser_dict


def main():
    plugins = Plugins()
    plugins.notify('focker_start')

    focker_lock()
    zfs_init()
    parser, parser_dict = create_parser()

    plugins.notify('focker_create_parser',
        parser=parser, parser_dict=parser_dict)

    args = parser.parse_args()
    plugins.notify('focker_parse_args', args=args)

    if not hasattr(args, 'func'):
        parser.print_usage()
        sys.exit('You must choose a mode')

    plugins.notify('focker_pre_' + args.func.__name__, args=args)
    args.func(args)
    plugins.notify('focker_post_' + args.func.__name__, args=args)

    plugins.notify('focker_quit', args=args)


if __name__ == '__main__':
    main()
