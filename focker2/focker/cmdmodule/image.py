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
    def provide_parsers(subp):
        parser = subp.add_parser('image', aliases=['ima', 'img', 'im', 'i'])
        subp = parser.add_subparsers()
        parser = subp.add_parser('build', aliases=['bld', 'b'])
        parser.set_defaults(func=cmd_image_build)
        parser = subp.add_parser('list', aliases=['lst', 'ls', 'l'])
        parser.set_defaults(func=cmd_image_list)


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
