#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from ..plugin import Plugin
from ..core import Image, \
    ImageBuilder
from .common import standard_fobject_commands


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
                        ),
                        atomic=dict(
                            aliases=['a'],
                            action='store_true'
                        )
                    )
                )
            )
        )


def cmd_image_build(args):
    bld = ImageBuilder(args.focker_dir, squeeze=args.squeeze, atomic=args.atomic)
    im = bld.build()
    im.add_tags(args.tags)
    print(f'Created {im.name}, mounted at {im.path}, with tags: {", ".join(args.tags)}')
