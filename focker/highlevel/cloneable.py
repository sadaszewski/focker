from ..zfs import zfs_list, \
    zfs_clone, \
    zfs_mountpoint
from ..zfs2 import zfs_exists_props, \
    zfs_shortest_unique_name
from .taggable import Taggable


class Cloneable:
    def __init__(self, **kwargs):
        pass
        
    @classmethod
    def from_base(cls, base: Taggable, sha256: str) -> Taggable:
        if not base.is_finalized:
            raise RuntimeError('Base must be finalized')
        if zfs_exists_props({ 'focker:sha256': sha256 }, focker_type=cls._meta_focker_type,
            zfs_type=cls._meta_zfs_type):
            raise RuntimeError(f'{cls.__name__} with specified SHA256 already exists')
        name = zfs_shortest_unique_name(sha256, focker_type=cls._meta_focker_type)
        zfs_clone(base.snapshot_name(), name, { 'focker:sha256': sha256 })
        mountpoint = zfs_mountpoint(name)
        return cls._meta_class(init_key=cls.__init_key, name=name, sha256=sha256,
            tags=[], mountpoint=mountpoint, is_finalized=False)

    def finalize(self):
        zfs_set_props(self.name, { 'rdonly': 'on' })
        zfs_snapshot(self.snapshot_name())
        self.is_finalized = True

    def snapshot_name(self):
        return self.name + '@1'
