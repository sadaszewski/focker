from ..plugin import Plugin
from argparse import ArgumentParser
from ..core import JailFs
from tabulate import tabulate
from .common import standard_fobject_commands
from ..core.process import focker_subprocess_check_output, \
    focker_subprocess_run


class JailPlugin(Plugin):
    @staticmethod
    def provide_parsers():
        return dict(
            jail=dict(
                aliases=['j'],
                subparsers=dict(
                    **standard_fobject_commands(JailFs),
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


def cmd_jail_exec(args):
    jfs = JailFs.from_any_id(args.identifier)
    focker_subprocess_run([ 'jexec', str(jfs.jid), args.command ])
