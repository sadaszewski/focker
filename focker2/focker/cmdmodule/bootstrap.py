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

    @staticmethod
    def extend_parsers():
        return dict(
            image=dict(
                subparsers=dict(
                    list=dict(
                        tree=dict(action='store_true')
                    )
                )
            )
        )


def cmd_bootstrap(args):
    raise NotImplementedError
