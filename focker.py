from argparse import ArgumentParser
import yaml
import os
# from weir import zfs, process
from .image import command_image_build
import sys
from .zfs import zfs_init


def create_parser():
    parser_top = ArgumentParser()
    subparsers_top = parser_top.add_subparsers()

    subparsers = subparsers_top.add_parser('image').add_subparsers()
    parser = subparsers.add_parser('build')
    parser.set_defaults(func=command_image_build)
    parser.add_argument('focker_dir', type=str)
    parser.add_argument('--tag', '-t', type=str, nargs='+', default=[])

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
