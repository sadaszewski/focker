from .jailspec import JailSpec
from ..jailfs import JailFs
from ..image import Image
from typing import Dict


class CloneImageJailSpec(JailSpec):
    @classmethod
    def from_dict(cls, jailspec: Dict):
        if 'image' not in jailspec:
            raise KeyError('image not specified')
        im = Image.from_any_id(jailspec['image'], strict=True)
        jfs = JailFs.clone_from(im)
        jailspec = dict(jailspec)
        del jailspec['image']
        jailspec['path'] = jfs.path
        jailspec['name'] = os.path.split(jfs.path)[-1]
        return cls._from_dict(jailspec)
