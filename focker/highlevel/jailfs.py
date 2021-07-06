from .image import Image
from .zfs import zfs_shortest_unique_name
from .taggable import Taggable
from .cloneable import Cloneable


JailFs = 'JailFs'

class JailFs(Taggable, Cloneable):
    _meta_focker_type = 'jail'
    _meta_cloneable_from = Image

    def __init__(self, **kwargs):
        Taggable.__init__(self, **kwargs)
        Cloneable.__init__(self, **kwargs)

    @staticmethod
    def from_image(image: Image, sha256: str) -> JailFs:
        return JailFs.clone_from(image, sha256)

        #if not image.is_finalized:
        #    raise RuntimeError('Image must be finalized')
        #if zfs_exists_props({ 'focker:sha256': sha256 }, focker_type='jail',
        #    zfs_type='filesystem'):
        #    raise RuntimeError('Jail with specified SHA256 already exists')
        #name = zfs_shortest_unique_name(sha256, focker_type='jail')
        #zfs_clone(image.snapshot_name(), name, { 'focker:sha256': sha256 })
        #mountpoint = zfs_mountpoint(name)
        #return JailFs(init_key=JailFs.__init_key, name=name, sha256=sha256,
        #    mountpoint=mountpoint)

    def path(self):
        return self.mountpoint

JailFs._meta_class = JailFs
