from ..plugin import Plugin
from .cmdmodule import CmdModule
from argparse import ArgumentParser
from ..core import Image
from tabulate import tabulate


class CmdModuleImagePlugin(Plugin):
    def provide_command_modules():
        return [ CmdModuleImage ]


class CmdModuleImage(CmdModule):
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
                            choices=['name', 'tags', 'sha256', 'mountpoint', 'is_finalized']
                        ),
                        sort=dict(
                            aliases=['s'],
                            type=str,
                            default=None,
                            choices=['name', 'tags', 'sha256', 'mountpoint', 'is_finalized']
                        )
                    )
                )
            )
        )
        #parser = subp.add_parser('image', aliases=['ima', 'img', 'im', 'i'])
        #subp = parser.add_subparsers()
        #parser = subp.add_parser('build', aliases=['bld', 'b'])
        #parser.set_defaults(func=cmd_image_build)
        #parser = subp.add_parser('list', aliases=['lst', 'ls', 'l'])
        #parser.set_defaults(func=cmd_image_list)


def cmd_image_build(args):
    raise NotImplementedError


def cmd_image_list(args):
    res = [ (' '.join(im.tags), im.mountpoint, ) for im in Image.list() ]
    print(tabulate(res, headers=['Tags', 'Mountpoint']))


def cmd_image_tag(args):
    raise NotImplementedError


def cmd_image_untag(args):
    raise NotImplementedError


def cmd_image_prune(args):
    raise NotImplementedError
