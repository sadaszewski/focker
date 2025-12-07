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
                        )
                    ),

                    rollback = dict(
                        aliases=['rb'],
                        func=cmd_volume_rollback,
                        reference=dict(
                            positional=True,
                            type=str
                        )
                    )
                )
            )
        )
    

def cmd_volume_snapshot_info(args):
    vol = Volume.from_any_id(args.reference)
    _, max_id = vol.list_snapshots()
    if max_id == 0:
        print("No snapshots.")
        return
    res = [ dict(tags=", ".join(vol.tags), name=f"{vol.name}@{i}") for i in range(1, max_id + 1) ]
    print(tabulate(res, headers=dict(name="Name", tags="Tags")))


def cmd_volume_snapshot(args):
    vol = Volume.from_any_id(args.reference)
    res = vol.snapshot()
    print(f"Snapshot made: {res}")


def cmd_volume_rollback(args):
    vol = Volume.from_any_id(args.reference)
    _, max_id = vol.list_snapshots()
    if max_id == 0:
        print("No snapshots to roll back")
        return
    vol.rollback()
    print(f"Rolled back and destroyed snapshot: {vol.name}@{max_id}")
