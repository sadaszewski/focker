from ..plugin import Plugin
from argparse import ArgumentParser
from ..core import JailFs
from tabulate import tabulate
from .common import cmd_taggable_list


class JailPlugin(Plugin):
    @staticmethod
    def provide_parsers():
        return dict(
            jail=dict(
                aliases=['j'],
                subparsers=dict(
                    list=dict(
                        aliases=['lst', 'ls', 'l'],
                        func=cmd_jail_list,
                        output=dict(
                            aliases=['o'],
                            type=str,
                            default=['tags', 'mountpoint'],
                            nargs='+',
                            choices=['name', 'tags', 'sha256', 'mountpoint']
                        ),
                        sort=dict(
                            aliases=['s'],
                            type=str,
                            default=None,
                            choices=['name', 'tags', 'sha256', 'mountpoint']
                        )
                    ),
                    exec=dict(
                        aliases=['exe', 'ex', 'e'],
                        func=cmd_jail_exec,
                        identifier=dict(
                            positional=True,
                            type=str
                        ),
                        command=dict(
                            aliases=['c'],
                            type=str,
                            default='/bin/sh'
                        )
                    )
                )
            )
        )


def cmd_jail_list(args):
    cmd_taggable_list(args, JailFs)


def cmd_jail_exec(args):
    raise NotImplementedError
