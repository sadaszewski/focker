from ...plugin import Plugin
from argparse import ArgumentParser
from ...core import Image
from tabulate import tabulate
from ..common import standard_fobject_commands
from .build import cmd_image_build


class ImagePlugin(Plugin):
    @staticmethod
    def provide_parsers():
        return dict(
            image=dict(
                aliases=['ima', 'img', 'im', 'i'],
                subparsers=dict(
                    **standard_fobject_commands(Image),
                    build=dict(
                        aliases=['bld', 'b'],
                        func=cmd_image_build,
                        focker_dir=dict(
                            positional=True,
                            type=str
                        ),
                        tags=dict(
                            aliases=['t'],
                            type=str,
                            nargs='+',
                            default=[]
                        ),
                        squeeze=dict(
                            aliases=['s'],
                            action='store_true'
                        )
                    )
                )
            )
        )
