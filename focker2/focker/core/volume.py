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
        for k, blk in conf.jail_blocks.items():
            for v in Volume.list():
                 if f'mount -t nullfs {v.path} ' in blk.safe_get('exec.prestart', ''):
                     used.add(v.path)
        lst = Volume.list()
        lst = [ v for v in lst if v.path not in used ]
        return lst

Volume._meta_class = Volume
