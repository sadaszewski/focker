from ..plugin import Plugin
from tabulate import tabulate
from .common import cmd_taggable_list
from ..core import Volume


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
                    )
                    #    command_volume_remove, \
                    #    command_volume_set, \
                    #    command_volume_get, \
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
