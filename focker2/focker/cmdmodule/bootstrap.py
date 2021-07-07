from ..plugin import Plugin
from .cmdmodule import CmdModule
from tabulate import tabulate


class CmdModuleBootstrapPlugin(Plugin):
    def provide_command_modules():
        return [ CmdModuleBootstrap ]


class CmdModuleBootstrap(CmdModule):
    @staticmethod
    def provide_parsers():
        return dict(
            bootstrap=dict(
                aliases=['boot', 'bs', 'b'],
                func=cmd_bootstrap
            )
        )


def cmd_bootstrap(args):
    raise NotImplementedError
