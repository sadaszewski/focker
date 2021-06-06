from .image import Image
from ..zfs2 import zfs_shortest_unique_name


class JailFs:
    __init_key = object()

    def __init__(self, **kwargs):
        if kwargs.get('init_key') != JailFs.__init_key:
            raise RuntimeError('JailFs must be created using one of the factory methods')

        self.name = kwargs['name']
        self.sha256 = kwargs['sha256']
        self.mountpoint = kwargs['mountpoint']

    @staticmethod
    def from_image(image: Image, sha256: str) -> Image:
        if not image.is_finalized:
            raise RuntimeError('Image must be finalized')
        if zfs_exists_props({ 'focker:sha256': sha256 }, focker_type='jail',
            zfs_type='filesystem'):
            raise RuntimeError('Jail with specified SHA256 already exists')
        name = zfs_shortest_unique_name(sha256, focker_type='jail')
        zfs_clone(image.snapshot_name(), name, { 'focker:sha256': sha256 })
        mountpoint = zfs_mountpoint(name)
        return JailFs(init_key=JailFs.__init_key, name=name, sha256=sha256,
            mountpoint=mountpoint)

    def path(self):
        return self.mountpoint
