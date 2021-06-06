from ..zfs import zfs_list, \
    zfs_clone, \
    zfs_mountpoint, \
    zfs_set_props, \
    zfs_tag, \
    zfs_untag
from ..zfs2 import zfs_shortest_unique_name, \
    zfs_snapshot, \
    zfs_exists_props
from ..snapshot import new_snapshot
from ..misc import find_prefix
from .taggable import Taggable

Image='Image'

class Image(Taggable):
    __init_key = object()
    _meta_focker_type = 'image'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def from_base(base: Image, sha256: str) -> Image:
        if not base.is_finalized:
            raise RuntimeError('Base must be finalized')
        if zfs_exists_props({ 'focker:sha256': sha256 }, focker_type='image',
            zfs_type='filesystem'):
            raise RuntimeError('Image with specified SHA256 already exists')
        name = zfs_shortest_unique_name(sha256, focker_type='image')
        zfs_clone(base.snapshot_name(), name, { 'focker:sha256': sha256 })
        mountpoint = zfs_mountpoint(name)
        return Image(init_key=Image.__init_key, name=name, sha256=sha256,
            tags=[], mountpoint=mountpoint, is_finalized=False)

    def apply_spec(self):
        raise NotImplementedError

    def finalize(self):
        zfs_set_props(self.name, { 'rdonly': 'on' })
        zfs_snapshot(self.snapshot_name())
        self.is_finalized = True

    def create(self):
        raise NotImplementedError

    def path(self):
        return self.mountpoint

    def snapshot_name(self):
        return self.name + '@1'

Image._meta_class = Image
