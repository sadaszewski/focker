from ..plugin import Plugin
from tabulate import tabulate
from .common import cmd_taggable_list
from ..core import Volume


class VolumePlugin(Plugin):
    @staticmethod
    def provide_parsers():
        return dict(
            volume=dict(
                aliases=['vol', 'v'],
                subparsers=dict(
                    list=dict(
                        aliases=['lst', 'ls', 'l'],
                        func=cmd_volume_list,
                        output=dict(
                            aliases=['o'],
                            type=str,
                            default=['tags', 'mountpoint', 'is_protected'],
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


def cmd_volume_list(args):
    cmd_taggable_list(args, Volume)
