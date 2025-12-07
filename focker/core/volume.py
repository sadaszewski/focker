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
        _= map(int, _)
        snapshots = list(_)
        max_id = max(snapshots, default=0)
        for i in range(1, max_id + 1):
            if i not in snapshots:
                raise ValueError("Non-contiguous snapshot numbering detected")
        return (snapshots, max_id)
    
    def snapshot(self):
        _, max_id = self.list_snapshots()
        new_id = max_id + 1
        zfs_snapshot(f"{self.name}@{new_id}")
        return f"{self.name}@{new_id}"
    
    def rollback(self):
        _, max_id = self.list_snapshots()
        if max_id == 0:
            raise ValueError("No snapshots to roll back.")
        zfs_rollback(f"{self.name}@{max_id}")
        zfs_destroy(f"{self.name}@{max_id}")
        

Volume._meta_class = Volume
