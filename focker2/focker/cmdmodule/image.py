from ..plugin import Plugin
from argparse import ArgumentParser
from ..core import Image
from tabulate import tabulate
from .common import cmd_taggable_list


class ImagePlugin(Plugin):
    @staticmethod
    def provide_parsers():
        return dict(
            image=dict(
                aliases=['ima', 'img', 'im', 'i'],
                subparsers=dict(
                    build=dict(
                        aliases=['bld', 'b'],
                        func=cmd_image_build
                    ),
                    list=dict(
                        aliases=['lst', 'ls', 'l'],
                        func=cmd_image_list,
                        output=dict(
                            aliases=['o'],
                            type=str,
                            default=['tags', 'mountpoint'],
                            nargs='+',
                            choices=['name', 'tags', 'sha256', 'mountpoint', 'is_finalized', 'is_protected']
                        ),
                        sort=dict(
                            aliases=['s'],
                            type=str,
                            default=None,
                            choices=['name', 'tags', 'sha256', 'mountpoint', 'is_finalized', 'is_protected']
                        )
                    )
                )
            )
        )


def cmd_image_build(args):
    raise NotImplementedError


def cmd_image_list(args):
    cmd_taggable_list(args, Image)


def cmd_image_tag(args):
    raise NotImplementedError


def cmd_image_untag(args):
    raise NotImplementedError


def cmd_image_prune(args):
    raise NotImplementedError
