#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from .image import Image
from .zfs import zfs_shortest_unique_name, \
    zfs_list
from .dataset import Dataset
from .process import focker_subprocess_check_output
from .misc import ensure_list
from .osjail import OSJail
import json


JailFs = 'JailFs'

class JailFs(Dataset):
    _meta_focker_type = 'jail'
    _meta_cloneable_from = Image

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def destroy(self, force=False):
        jail = OSJail.from_mountpoint(self.path, raise_exc=False)
        if jail is not None:
            jail.remove()
        super().destroy(force=force)

    @property
    def jid(self):
        j = OSJail.from_mountpoint(self.mountpoint, raise_exc=False)
        if j is None:
            return None
        return j.jid

    @staticmethod
    def list_unused():
        conf, lst = load_jailconf(return_jfs_list=True)
        used = set()
        for k, v in conf.items():
            for jname in v.get('depend', []):
                if jname not in conf:
                    continue
                used.add(conf[jname]['path'])
        lst = [ JailFs.from_name(name) \
            for name, mountpoint, *_ in lst \
                if mountpoint not in used ]
        return lst

JailFs._meta_class = JailFs
