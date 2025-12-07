#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from ..plugin import Plugin
from tabulate import tabulate
from .common import standard_fobject_commands
from ..core import Volume
from ..core.zfs import zfs_list, zfs_snapshot, zfs_rollback, zfs_destroy
from operator import itemgetter, methodcaller


class VolumePlugin(Plugin):
    @staticmethod
    def provide_parsers():
        return dict(
            volume=dict(
                aliases=['vol', 'v'],
                subparsers=dict(
                    **standard_fobject_commands(Volume),

                    snapshot_info = dict(
                        aliases=['si'],
                        func=cmd_volume_snapshot_info,
                        reference=dict(
                            positional=True,
                            type=str
                        )
                    ),

                    snapshot = dict(
                        aliases=['ss'],
                        func=cmd_volume_snapshot,
                        reference=dict(
                            positional=True,
                            type=str
                        ),
                        snapshot_name=dict(
                            positional=True,
                            type=str
                        )
                    ),

                    rollback = dict(
                        aliases=['rb'],
                        func=cmd_volume_rollback,
                        reference=dict(
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

                    snapshot_destroy = dict(
                        aliases=['sd'],
                        func=cmd_volume_snapshot_destroy,
                        reference=dict(
                            positional=True,
                            type=str
                        ),
                        snapshot_name=dict(
                            positional=True,
                            type=str
                        )
                    ),

                    rollback_destroy = dict(
                        aliases=['rbd'],
                        func=cmd_volume_rollback_destroy,
                        reference=dict(
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
                    )
                )
            )
        )
    

def cmd_volume_snapshot_info(args):
    vol = Volume.from_any_id(args.reference)
    snapshots = vol.list_snapshots()
    if len(snapshots) == 0:
        print("No snapshots.")
        return
    res = [ dict(tags=", ".join(vol.tags), name=f"{vol.name}@{s}") for s in snapshots ]
    print(tabulate(res, headers=dict(name="Name", tags="Tags")))


def cmd_volume_snapshot(args):
    vol = Volume.from_any_id(args.reference)
    vol.snapshot(args.snapshot_name)
    print(f"Snapshot made: {vol.name}@{args.snapshot_name}")


def cmd_volume_rollback(args):
    vol = Volume.from_any_id(args.reference)
    snapshots = vol.list_snapshots()
    if len(snapshots) == 0:
        print("No snapshots to roll back.")
        return
    if args.snapshot_name not in snapshots:
        print("Snapshot name not found.")
        return
    if args.force:
        print("Using -r: more recent snapshots will be destroyed")
    vol.rollback(args.snapshot_name, force=args.force)
    print(f"Rolled back snapshot: {vol.name}@{args.snapshot_name}")


def cmd_volume_snapshot_destroy(args):
    vol = Volume.from_any_id(args.reference)
    snapshots = vol.list_snapshots()
    if len(snapshots) == 0:
        print("No snapshots to destroy.")
        return
    if args.snapshot_name not in snapshots:
        print("Snapshot name not found.")
        return
    vol.snapshot_destroy(args.snapshot_name)
    print(f"Snapshot destroyed: {vol.name}@{args.snapshot_name}")


def cmd_volume_rollback_destroy(args):
    cmd_volume_rollback(args)
    cmd_volume_snapshot_destroy(args)
