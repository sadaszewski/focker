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
from ..misc import load_jailconf, \
    save_jailconf


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
        conf = load_jailconf()
        used = set()
        for k, v in conf.jail_blocks.items():
            for jname in ensure_list(v.safe_get('depend', [])):
                if jname not in conf:
                    continue
                used.add(conf[jname]['path'])
        lst = zfs_list(['name', 'mountpoint'], focker_type='jail')
        lst = [ JailFs.from_name(item[0]) for item in lst if item[1] not in used ]
        return lst

JailFs._meta_class = JailFs
