from ..plugin import Plugin
from tabulate import tabulate
from .common import cmd_taggable_list
from ..core import Volume
import argparse


class VolumePlugin(Plugin):
    @staticmethod
    def provide_parsers():
        return dict(
            volume=dict(
                aliases=['vol', 'v'],
                subparsers=dict(
                    list=dict(
                        aliases=['lst', 'ls', 'l'],
                        func=cmd_volume_list,
                        output=dict(
                            aliases=['o'],
                            type=str,
                            default=['tags', 'mountpoint', 'is_protected'],
                            nargs='+',
                            choices=['name', 'tags', 'sha256', 'mountpoint', 'is_protected']
                        ),
                        sort=dict(
                            aliases=['s'],
                            type=str,
                            default=None,
                            choices=['name', 'tags', 'sha256', 'mountpoint', 'is_protected']
                        )
                    ),
                    create=dict(
                        aliases=['creat', 'crea', 'cre', 'c'],
                        func=cmd_volume_create,
                        tags=dict(
                            aliases=['t'],
                            type=str,
                            nargs='+'
                        )
                    ),
                    prune=dict(
                        aliases=['pru', 'p'],
                        func=cmd_volume_prune
                    ),
                    tag=dict(
                        aliases=['t'],
                        func=cmd_volume_tag,
                        reference=dict(
                            positional=True,
                            type=str
                        ),
                        tags=dict(
                            positional=True,
                            type=str,
                            nargs='+'
                        )
                    ),
                    untag=dict(
                        aliases=['u'],
                        func=cmd_volume_untag,
                        tags=dict(
                            positional=True,
                            nargs='+'
                        )
                    ),
                    remove=dict(
                        aliases=['rm', 'r'],
                        func=cmd_volume_remove,
                        reference=dict(
                            positional=True,
                            type=str
                        )
                    ),
                    set=dict(
                        func=cmd_volume_set,
                        reference=dict(
                            positional=True,
                            type=str
                        ),
                        properties=dict(
                            positional=True,
                            type=str,
                            nargs=argparse.REMAINDER
                        )
                    ),
                    get=dict(
                        func=cmd_volume_get,
                        reference=dict(
                            positional=True,
                            type=str
                        ),
                        properties=dict(
                            positional=True,
                            type=str,
                            nargs=argparse.REMAINDER
                        )
                    )
                    #    command_volume_protect, \
                    #    command_volume_unprotect
                )
            )
        )

def cmd_volume_list(args):
    cmd_taggable_list(args, Volume)


def cmd_volume_create(args):
    v = Volume.create()
    v.add_tags(args.tags)
    print('Created', v.name, 'mounted at', v.path)


def cmd_volume_prune(args):
    Volume.prune()


def cmd_volume_tag(args):
    v = Volume.from_any_id(args.reference)
    v.add_tags(args.tags)


def cmd_volume_untag(args):
    Volume.untag(args.tags)


def cmd_volume_remove(args):
    v = Volume.from_any_id(args.reference)
    v.destroy()


def cmd_volume_set(args):
    v = Volume.from_any_id(args.reference)
    if not args.properties:
        raise ValueError('You must specify some properties')
    props = { p.split('=')[0]: '='.join(p.split('=')[1:]) for p in args.properties }
    v.set_props(props)


def cmd_volume_get(args):
    v = Volume.from_any_id(args.reference)
    if not args.properties:
        raise ValueError('You must specify some properties')
    res = v.get_props(args.properties)
    res = [ [ k, res[k] ] for k in args.properties ]
    print(tabulate(res, headers=['Property', 'Value']))
