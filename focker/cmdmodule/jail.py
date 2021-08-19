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
    OneExecJailSpec, \
    TemporaryOSJail, \
    CloneImageJailSpec
from ..core.jailspec import JailSpec
from .common import standard_fobject_commands
from contextlib import ExitStack


class JailPlugin(Plugin):
    @staticmethod
    def provide_parsers():
        return dict(
            jail=dict(
                aliases=['j'],
                subparsers=dict(
                    **standard_fobject_commands(JailFs),
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
    spec = OneExecJailSpec.from_image_and_dict(im, {})
    with ExitStack() as stack, \
        TemporaryOSJail(spec) as jail:
        stack.callback(spec.jfs.destroy)
        if args.chkout:
            print(jail.check_output(args.command))
        else:
            jail.run(args.command) # pragma: no cover


def cmd_jail_fromimage(args):
    params = { p.split('=')[0]: '='.join(p.split('=')[1:]) for p in args.params }
    spec = CloneImageJailSpec.from_dict({ 'image': args.image_reference, **params })
    spec.jfs.add_tags(args.tags)
    ospec = OSJailSpec.from_jailspec(spec)
    ospec.add()
    print('Added jail', ospec.name, 'with path', spec.jfs.path)
