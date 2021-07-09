from .image import Image
from .zfs import zfs_shortest_unique_name
from .taggable import Taggable
from .cloneable import Cloneable
from .process import focker_subprocess_check_output
import json


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

    #def path(self):
    #    return self.mountpoint

    @property
    def jid(self):
        info = focker_subprocess_check_output([ 'jls', '--libxo',  'json' ])
        info = json.loads(info)
        info = [ j for j in info['jail-information']['jail']
            if j['path'] == self.path ]
        if len(info) == 0:
            return None
        if len(info) == 1:
            return info[0]['jid']
        raise RuntimeError('Multiple jails with the same path - unsupported')

JailFs._meta_class = JailFs
