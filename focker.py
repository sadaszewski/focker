from argparse import ArgumentParser
import yaml
import os
# from weir import zfs, process
from .image import command_image_build, \
    command_image_untag, \
    command_image_list, \
    command_image_prune
import sys
from .zfs import zfs_init
from .jail import command_jail_run


def create_parser():
    parser_top = ArgumentParser()
    subparsers_top = parser_top.add_subparsers()

    subparsers = subparsers_top.add_parser('image').add_subparsers()
    parser = subparsers.add_parser('build')
    parser.set_defaults(func=command_image_build)
    parser.add_argument('focker_dir', type=str)
    parser.add_argument('--tag', '-t', type=str, nargs='+', default=[])

    parser = subparsers.add_parser('untag')
    parser.set_defaults(func=command_image_untag)
    parser.add_argument('tags', type=str, nargs='+', default=[])

    parser = subparsers.add_parser('list')
    parser.set_defaults(func=command_image_list)
    parser.add_argument('--full-sha256', '-f', action='store_true')

    parser = subparsers.add_parser('prune')
    parser.set_defaults(func=command_image_prune)

    subparsers = subparsers_top.add_parser('jail').add_subparsers()
    parser = subparsers.add_parser('run')
    parser.set_defaults(func=command_jail_run)
    parser.add_argument('image', type=str)
    parser.add_argument('--command', '-c', type=str, default='/bin/sh')

    return parser_top


def main():
    zfs_init()
    parser = create_parser()
    args = parser.parse_args()
    if not hasattr(args, 'func'):
        sys.exit('You must choose a mode')
    args.func(args)

if __name__ == '__main__':
    main()
