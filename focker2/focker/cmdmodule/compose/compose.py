#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from ...plugin import Plugin
from .image import build_images
from .volume import build_volumes
from .jail import build_jails
from .hook import exec_prebuild, \
    exec_postbuild
from ... import yaml
import os


class ComposePlugin(Plugin):
    @staticmethod
    def provide_parsers():
        return dict(
            compose=dict(
                aliases=['comp', 'cmp', 'c'],
                subparsers=dict(
                    build=dict(
                        aliases=['bld', 'b'],
                        func=cmd_compose_build,
                        spec_filename=dict(
                            positional=True,
                            type=str
                        ),
                        squeeze=dict(
                            action='store_true'
                        )
                    )
                )
            )
        )


def cmd_compose_build(args):
    with open(args.spec_filename, 'r') as f:
        spec = yaml.safe_load(f)

    spec_dir, _ = os.path.split(args.spec_filename)

    exec_prebuild(spec.get('exec.prebuild', []), spec_dir)
    build_images(spec.get('images', {}), spec_dir, squeeze=args.squeeze)
    build_volumes(spec.get('volumes', {}))
    if 'jails' in spec:
        build_jails(spec['jails'])
    exec_postbuild(spec.get('exec.postbuild', []), spec_dir)
