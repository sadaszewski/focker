#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from ..dataset import Dataset
from ..zfs import zfs_list


Image='Image'

class Image(Dataset):
    _meta_focker_type = 'image'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def list_unused():
        fields = ['name', 'origin']
        lst = zfs_list(fields, focker_type='image') + \
            zfs_list(fields, focker_type='jail')
        used = set()
        for item in lst:
            used.add(item[1].split('@')[0])
        lst = zfs_list(fields, focker_type='image')
        lst = [ Image.from_name(item[0]) for item in lst if item[0] not in used ]
        return lst

Image._meta_class = Image
Image._meta_cloneable_from = Image