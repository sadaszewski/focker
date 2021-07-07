from ..plugin import Plugin
from tabulate import tabulate


class BootstrapPlugin(Plugin):
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
