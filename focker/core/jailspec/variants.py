#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from .jailspec import JailSpec
from ..jailfs import JailFs
from ..image import Image
from typing import Dict
import os


class CloneImageJailSpec(JailSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.jfs = None

    @classmethod
    def from_dict(cls, jailspec: Dict = {}):
        if 'image' not in jailspec:
            raise KeyError('Image not specified')
        im = Image.from_any_id(jailspec['image'], strict=True)
        jfs = JailFs.clone_from(im)
        jailspec = dict(jailspec)
        del jailspec['image']
        jailspec['path'] = jfs.path
        name = os.path.split(jfs.path)[-1]
        if 'name' not in jailspec:
            jailspec['name'] = name
        if 'host.hostname' not in jailspec:
            jailspec['host.hostname'] = name
        res = cls._from_dict(jailspec)
        res.jfs = jfs
        return res


class ImageBuildJailSpec(JailSpec):
    @classmethod
    def from_image_and_dict(cls, im: Image, jailspec: Dict = {}):
        if 'image' in jailspec:
            raise KeyError('image should be specified separately')
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
            raise KeyError('image should be specified separately')
        jfs = JailFs.clone_from(im)
        jailspec = dict(jailspec)
        jailspec['path'] = jfs.path
        name = os.path.split(jfs.path)[-1]
        jailspec['name'] = 'one_' + name
        jailspec['host.hostname'] = name
        res = cls._from_dict(jailspec)
        res.jfs = jfs
        return res
