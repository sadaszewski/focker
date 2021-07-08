from ..plugin import Plugin
from tabulate import tabulate
from ..core.zfs import zfs_init


class BootstrapPlugin(Plugin):
    @staticmethod
    def provide_parsers():
        return dict(
            bootstrap=dict(
                aliases=['boot', 'bs', 'b'],
                subparsers=dict(
                    filesystem=dict(
                        aliases=['fs'],
                        func=cmd_bootstrap_filesystem
                    )
                )
            )
        )


def cmd_bootstrap_filesystem(args):
    print('Creating necessary filesystem objects...')
    zfs_init()
    print('Done.')
