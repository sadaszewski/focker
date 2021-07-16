from ...plugin import Plugin
from .image import build_images
from .volume import build_volumes
from .jail import build_jails
import ruamel.yaml as yaml


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
                        )
                    )
                )
            )
        )


def cmd_compose_build(args):
    with open(args.spec_filename, 'r') as f:
        spec = yaml.safe_load(f)

    build_volumes(spec.get('volumes', {}))
    build_images(spec.get('images', {}))
    build_jails(spec.get('jails', {}))
