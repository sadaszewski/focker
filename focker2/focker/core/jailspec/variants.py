from .jailspec import JailSpec
from ..jailfs import JailFs
from ..image import Image
from typing import Dict
import os


class CloneImageJailSpec(JailSpec):
    @classmethod
    def from_dict(cls, jailspec: Dict = {}):
        if 'image' not in jailspec:
            raise KeyError('image not specified')
        im = Image.from_any_id(jailspec['image'], strict=True)
        jfs = JailFs.clone_from(im)
        jailspec = dict(jailspec)
        del jailspec['image']
        jailspec['path'] = jfs.path
        name = os.path.split(jfs.path)[-1]
        jailspec['name'] = name
        jailspec['host.hostname'] = name
        return cls._from_dict(jailspec)


class ImageBuildJailSpec(JailSpec):
    @classmethod
    def from_image_and_dict(cls, im: Image, jailspec: Dict = {}):
        if 'image' in jailspec:
            raise RuntimeError('image should be specified separately')
        jailspec = dict(jailspec)
        jailspec['path'] = im.path
        name = os.path.split(im.path)[-1]
        jailspec['name'] = 'img_' + name
        jailspec['host.hostname'] = name
        jailspec['exec.start'] = ''
        jailspec['exec.stop'] = ''
        return cls._from_dict(jailspec)


class OneExecJailSpec(JailSpec):
    @classmethod
    def from_image_and_dict(cls, im: Image, jailspec: Dict = {}):
        if 'image' in jailspec:
            raise RuntimeError('image should be specified separately')
        jfs = JailFs.clone_from(im)
        jailspec = dict(jailspec)
        jailspec['path'] = jfs.path
        name = os.path.split(jfs.path)[-1]
        jailspec['name'] = 'one_' + name
        jailspec['host.hostname'] = name
        return cls._from_dict(jailspec)
