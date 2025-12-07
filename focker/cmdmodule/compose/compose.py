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
from ...core import OSJail
import os
from ...core import Volume


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
                    ),

                    snapshot=dict(
                        aliases=['ss'],
                        func=cmd_compose_snapshot,
                        spec_filename=dict(
                            positional=True,
                            type=str
                        ),
                        snapshot_name=dict(
                            positional=True,
                            type=str
                        )
                    ),

                    rollback_destroy=dict(
                        aliases=['rbd'],
                        func=cmd_compose_rollback_destroy,
                        spec_filename=dict(
                            positional=True,
                            type=str
                        ),
                        snapshot_name=dict(
                            positional=True,
                            type=str
                        )
                    ),

                    stop=dict(
                        func=cmd_compose_stop,
                        spec_filename=dict(
                            positional=True,
                            type=str
                        )
                    ),

                    start=dict(
                        func=cmd_compose_start,
                        spec_filename=dict(
                            positional=True,
                            type=str
                        )
                    ),
                )
            )
        )

    
def stop_jails(jail_refs):
    for ref in jail_refs:
        j = OSJail.from_any_id(ref, raise_exc=False)
        if j is None:
            continue
        if j.is_running:
            j.stop()


def start_jails(jail_refs):
    for ref in jail_refs:
        j = OSJail.from_any_id(ref, raise_exc=False)
        if j is None:
            continue
        if not j.is_running:
            j.start()


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


def cmd_compose_snapshot(args):
    with open(args.spec_filename, 'r') as f:
        spec = yaml.safe_load(f)

    stop_jails(spec.get('jails', {}).keys())

    for tag in spec.get('volumes', {}).keys():
        v = Volume.from_tag(tag)
        res = v.snapshot(args.snapshot_name)
        print(f"Volume snapshot created: {res}")


def cmd_compose_rollback_destroy(args):
    with open(args.spec_filename, 'r') as f:
        spec = yaml.safe_load(f)

    stop_jails(spec.get('jails', {}).keys())

    for tag in spec.get('volumes', {}).keys():
        v = Volume.from_tag(tag)
        v.rollback(args.snapshot_name)
        res = v.snapshot_destroy(args.snapshot_name)
        print(f"Volume snapshot rolled back and destroyed: {res}")


def cmd_compose_stop(args):
    with open(args.spec_filename, 'r') as f:
        spec = yaml.safe_load(f)

    if len(spec.get('jails', {})) == 0:
        print("No jails to stop.")
        return

    stop_jails(spec.get('jails', {}).keys())
    print("Jails stopped.")


def cmd_compose_start(args):
    with open(args.spec_filename, 'r') as f:
        spec = yaml.safe_load(f)

    if len(spec.get('jails', {})) == 0:
        print("No jails to start.")
        return

    start_jails(spec.get('jails', {}).keys())
    print("Jails started.")
