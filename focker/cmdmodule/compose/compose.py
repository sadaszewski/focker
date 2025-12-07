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
from ...core import Volume, JailFs
from pathlib import Path
import json


class ComposePlugin(Plugin):
    @staticmethod
    def provide_parsers():
        return dict(
            compose=dict(
                aliases=['comp', 'cmp', 'c'],
                subparsers=dict(
                    info=dict(
                        aliases=['i'],
                        func=cmd_compose_info,
                        spec_filename=dict(
                            positional=True,
                            type=str
                        ),
                        raw=dict(
                            aliases=['r'],
                            action='store_true'
                        )
                    ),

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
                        ),
                        force=dict(
                            aliases=['f'],
                            action='store_true'
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


def deep_update(d_1: dict, d_2: dict):
    for k, v in d_2.items():
        if k in d_1 and isinstance(d_1[k], dict):
            deep_update(d_1[k], v)
        else:
            d_1[k] = v


def load_spec(filename: str):
    with open(filename, 'r') as f:
        spec = yaml.safe_load(f)

    if 'base' in spec:
        base = Path(spec['base'])
        if not base.is_absolute():
            base = Path(filename).parent / base
        base = base.resolve()
        base = load_spec(base)
        deep_update(base, spec)
        spec = base

    if 'prefix' in spec:
        prefix = spec['prefix']
        spec['volumes'] = { f'{prefix}{k}': v for k, v in spec.get('volumes', {}).items() }
        spec['jails'] = { f'{prefix}{k}': v for k, v in spec.get('jails', {}).items() }
        for jspec in spec.get('jails', {}).values():
            jspec['mounts'] = {
                (k if k.startswith("/") else f"{prefix}{k}"): v
                    for k, v in jspec.get('mounts', {}).items()
            }
            jspec['depend'] = [ f"{prefix}{d}" for d in jspec.get('depend', []) ]

    return spec

    
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


def cmd_compose_info(args):
    if args.raw:
        with open(args.spec_filename, 'r') as f:
            spec = yaml.safe_load(f)
    else:
        spec = load_spec(args.spec_filename)
    print(json.dumps(spec, indent=4))


def cmd_compose_build(args):
    spec = load_spec(args.spec_filename)

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
    spec = load_spec(args.spec_filename)

    stop_jails(spec.get('jails', {}).keys())

    for key, cls in [('volumes', Volume), ('jails', JailFs)]:
        for tag in spec.get(key, {}).keys():
            obj = cls.from_tag(tag)
            res = obj.snapshot(args.snapshot_name)
            print(f"{cls.__name__} snapshot created: {res}")


def cmd_compose_rollback_destroy(args):
    spec = load_spec(args.spec_filename)

    stop_jails(spec.get('jails', {}).keys())

    for key, cls in [('volumes', Volume), ('jails', JailFs)]:
        for tag in spec.get(key, {}).keys():
            obj = cls.from_tag(tag)
            obj.rollback(args.snapshot_name, force=args.force)
            res = obj.snapshot_destroy(args.snapshot_name)
            print(f"{cls.__name__} snapshot rolled back and destroyed: {res}")


def cmd_compose_stop(args):
    spec = load_spec(args.spec_filename)

    if len(spec.get('jails', {})) == 0:
        print("No jails to stop.")
        return

    stop_jails(spec.get('jails', {}).keys())
    print("Jails stopped.")


def cmd_compose_start(args):
    spec = load_spec(args.spec_filename)

    if len(spec.get('jails', {})) == 0:
        print("No jails to start.")
        return

    start_jails(spec.get('jails', {}).keys())
    print("Jails started.")
