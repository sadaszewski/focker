#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from .dataset import Dataset
from ..misc import load_jailconf
from .zfs import zfs_list, zfs_snapshot, zfs_rollback, zfs_destroy
from operator import itemgetter, attrgetter, methodcaller


class Volume(Dataset):
    _meta_focker_type = 'volume'
    _meta_can_finalize = False

    @classmethod
    def list_unused(cls):
        conf = load_jailconf()
        used = set()
        for k, blk in conf.items():
            for v in Volume.list():
                 if f'mount -t nullfs {v.path} ' in blk.get('exec.prestart', ''):
                     used.add(v.path)
        lst = Volume.list()
        lst = [ v for v in lst if v.path not in used ]
        return lst
    
    def list_snapshots(self):
        _= zfs_list(focker_type='volume', zfs_type='snapshot')
        _= map(itemgetter(0), _)
        _= filter(methodcaller("startswith", f"{self.name}@"), _)
        _= map(methodcaller("split", "@"), _)
        _= map(itemgetter(1), _)
        snapshots = list(_)
        return snapshots
    
    def snapshot(self, snapshot_name: str):
        snapshots = self.list_snapshots()
        if snapshot_name in snapshots:
            raise ValueError("Snapshot with that name already exists")
        zfs_snapshot(f"{self.name}@{snapshot_name}")
        return f"{self.name}@{snapshot_name}"
    
    def rollback(self, snapshot_name: str, force: bool = False):
        snapshots = self.list_snapshots()
        if snapshot_name not in snapshots:
            raise ValueError("Snapshot name not found.")
        zfs_rollback(f"{self.name}@{snapshot_name}", force=force)
        return f"{self.name}@{snapshot_name}"

    def snapshot_destroy(self, snapshot_name: str):
        snapshots = self.list_snapshots()
        if snapshot_name not in snapshots:
            raise ValueError("Snapshot name not found.")
        zfs_destroy(f"{self.name}@{snapshot_name}")
        return f"{self.name}@{snapshot_name}"
        

Volume._meta_class = Volume
