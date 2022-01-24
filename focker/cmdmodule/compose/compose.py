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
from ...core.fenv import fenv_from_arg, \
    fenv_from_spec
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
                        ),
                        fenv=dict(
                            aliases=['e'],
                            type=str,
                            nargs='+'
                        )
                    )
                )
            )
        )

    
def stop_jails(jail_refs):
    for ref in jail_refs:
        j = OSJail.from_any_id(ref)
        if j.is_running:
            j.stop()
    

def cmd_compose_build(args):
    with open(args.spec_filename, 'r') as f:
        spec = yaml.safe_load(f)

    spec_dir, _ = os.path.split(args.spec_filename)

    fenv = fenv_from_arg(args.fenv, {})
    fenv = fenv_from_spec(spec, fenv)

    stop_jails(spec.get('jails', {}).keys())
    exec_prebuild(spec.get('exec.prebuild', []), spec_dir, fenv=fenv)
    build_images(spec.get('images', {}), spec_dir, fenv=fenv, squeeze=args.squeeze)
    build_volumes(spec.get('volumes', {}), fenv=fenv)
    if 'jails' in spec:
        build_jails(spec['jails'], fenv=fenv)
    exec_postbuild(spec.get('exec.postbuild', []), spec_dir, fenv=fenv)
