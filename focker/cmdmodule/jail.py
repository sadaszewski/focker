#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from ..plugin import Plugin
import argparse
from ..core import JailFs, \
    Image, \
    OSJailSpec, \
    OSJail, \
    one_exec_jailspec, \
    TemporaryOSJail, \
    clone_image_jailspec
from ..core.jailspec import JailSpec
from .common import standard_fobject_commands, \
    DISPLAY_FIELDS, \
    DEFAULT_DISPLAY_FIELDS
from contextlib import ExitStack


class JailPlugin(Plugin):
    @staticmethod
    def provide_parsers():
        return dict(
            jail=dict(
                aliases=['j'],
                subparsers=dict(
                    **standard_fobject_commands(JailFs,
                        display_fields=DISPLAY_FIELDS + ['jid'],
                        default_display_fields=DEFAULT_DISPLAY_FIELDS + ['jid']),
                    exec=dict(
                        aliases=['exe', 'ex', 'e'],
                        func=cmd_jail_exec,
                        chkout=dict(
                            aliases=['c'],
                            action='store_true'
                        ),
                        identifier=dict(
                            positional=True,
                            type=str
                        ),
                        command=dict(
                            positional=True,
                            nargs='*',
                            type=str,
                            default=[ '/bin/sh' ]
                        )
                    ),
                    oneexec=dict(
                        aliases=['one', 'oe', 'o'],
                        func=cmd_jail_oneexec,
                        chkout=dict(
                            aliases=['c'],
                            action='store_true'
                        ),
                        mounts=dict(
                            aliases=['m'],
                            nargs='+',
                            type=str,
                            default=[]
                        ),
                        identifier=dict(
                            positional=True,
                            type=str
                        ),
                        command=dict(
                            positional=True,
                            nargs='*',
                            type=str,
                            default=[ '/bin/sh' ]
                        )
                    ),
                    fromimage=dict(
                        aliases=['fromimg', 'from', 'fi', 'f'],
                        func=cmd_jail_fromimage,
                        image_reference=dict(
                            positional=True,
                            type=str
                        ),
                        tags=dict(
                            aliases=['t'],
                            type=str,
                            nargs='+'
                        ),
                        params=dict(
                            positional=True,
                            type=str,
                            nargs='*',
                            default=[]
                        )
                    ),
                    start=dict(
                        aliases=['sta', 's'],
                        func=cmd_jail_start,
                        jail_reference=dict(
                            positional=True,
                            type=str
                        )
                    ),
                    stop=dict(
                        aliases=['sto', 'S'],
                        func=cmd_jail_stop,
                        jail_reference=dict(
                            positional=True,
                            type=str
                        )
                    ),
                    restart=dict(
                        aliases=['re', 'r'],
                        func=cmd_jail_restart,
                        jail_reference=dict(
                            positional=True,
                            type=str
                        )
                    )
                )
            )
        )


def cmd_jail_exec(args):
    jfs = JailFs.from_any_id(args.identifier)
    j = OSJail.from_mountpoint(jfs.path)
    if args.chkout:
        print(j.check_output(args.command))
    else:
        j.run(args.command)


def cmd_jail_oneexec(args):
    im = Image.from_any_id(args.identifier)
    mounts = {}
    for m in args.mounts:
        k, v = m.split(':')
        mounts[k] = v
    with one_exec_jailspec(im, { 'mounts': mounts }) as (spec, *_), \
        TemporaryOSJail(spec) as jail:
            if args.chkout:
                print(jail.check_output(args.command))
            else:
                jail.run(args.command) # pragma: no cover


def cmd_jail_fromimage(args):
    params = { p.split('=')[0]: '='.join(p.split('=')[1:]) for p in args.params }
    with clone_image_jailspec({ 'image': args.image_reference, **params }) as (spec, _, jfs_take_ownership):
        jfs = jfs_take_ownership()
        jfs.add_tags(args.tags)
        ospec = OSJailSpec.from_jailspec(spec)
        ospec.add()
        print('Added jail', ospec.name, 'with path', jfs.path)


def cmd_jail_start(args):
    j = OSJail.from_any_id(args.jail_reference)
    j.start()


def cmd_jail_stop(args):
    j = OSJail.from_any_id(args.jail_reference)
    j.stop()


def cmd_jail_restart(args):
    cmd_jail_stop(args)
    cmd_jail_start(args)
