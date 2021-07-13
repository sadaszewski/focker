from ..plugin import Plugin
from tabulate import tabulate
from .common import standard_fobject_commands
from ..core import Volume


class VolumePlugin(Plugin):
    @staticmethod
    def provide_parsers():
        return dict(
            volume=dict(
                aliases=['vol', 'v'],
                subparsers=standard_fobject_commands(Volume)
            )
        )
