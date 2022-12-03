#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from .dataset import Dataset
from ..misc import load_jailconf
from .zfs import zfs_list


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

Volume._meta_class = Volume
