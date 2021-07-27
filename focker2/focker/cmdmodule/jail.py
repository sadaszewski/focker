from ..plugin import Plugin
import argparse
from ..core import JailFs, \
    Image, \
    JailSpec, \
    OSJailSpec, \
    OSJail
from .common import standard_fobject_commands


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
                            nargs=argparse.REMAINDER
                        )
                    )
                )
            )
        )


def cmd_jail_exec(args):
    jfs = JailFs.from_any_id(args.identifier)
    j = OSJail.from_mountpoint(jfs.path)
    j.run(args.command)


def cmd_jail_fromimage(args):
    im = Image.from_any_id(args.image_reference)
    jfs = JailFs.clone_from(im)
    jfs.add_tags(args.tags)
    params = { p.split('=')[0]: '='.join(p.split('=')[1:]) for p in args.params }
    spec = JailSpec.from_dict(dict(jailfs=jfs, **params))
    ospec = OSJailSpec.from_jailspec(spec)
    ospec.add()
    print('Added jail', ospec.name, 'with path', jfs.path)
