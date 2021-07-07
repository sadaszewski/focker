from ..plugin import Plugin
from .cmdmodule import CmdModule
from argparse import ArgumentParser


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
