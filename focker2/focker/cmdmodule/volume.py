from ..plugin import Plugin
from .cmdmodule import CmdModule
from tabulate import tabulate


class CmdModuleVolumePlugin(Plugin):
    def provide_command_modules():
        return [ CmdModuleVolume ]


class CmdModuleVolume(CmdModule):
    @staticmethod
    def provide_parsers():
        return dict(
            volume=dict(
                aliases=['vol', 'v'],
                subparsers=dict(
                    list=dict(
                        aliases=['lst', 'ls', 'l'],
                        func=cmd_volume_list
                    )
                )
            )
        )


def cmd_volume_list(args):
    raise NotImplementedError
