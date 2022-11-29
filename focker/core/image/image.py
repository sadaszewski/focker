#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from ..dataset import Dataset
from ..zfs import zfs_list, \
    zfs_destroy
from functools import reduce


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

    @staticmethod
    def prune():
        fields = [ 'name', 'origin', 'focker:tags' ]
        tree = {}
        for focker_type in [ 'image', 'jail' ]:
            lst = zfs_list(fields, focker_type=focker_type)
            for name, origin, tags, *_ in lst:
                origin = origin.split('@')[0]
                node = tree.get(origin, {})
                children = node.get('children', [])
                children.append(name)
                node['children'] = children
                tree[origin] = node
                if focker_type == 'image' and tags == '-':
                    node = tree.get(name, {})
                    node.update({ 'parent': origin, 'tags': tags })
                    tree[name] = node
        batches = []
        while True:
            bat = set([ k for k, v in tree.items() if not v.get('children') ])
            if not bat:
                break
            batches.append(bat)
            tree = { k: v for k, v in tree.items() if k not in bat }
            for name in bat:
                for v in tree.values():
                    if name in v.get('children', []):
                        v['children'].remove(name)
        batches = reduce(list.__add__, map(list, batches), [])
        for name in batches:
            zfs_destroy(name)

Image._meta_class = Image
Image._meta_cloneable_from = Image
