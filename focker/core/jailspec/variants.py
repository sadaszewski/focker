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
from contextlib import ExitStack


class clone_image_jailspec:
    def __init__(self, jailspec: Dict):
        self.jailspec = jailspec
        self.jfs = None

    def __enter__(self):
        if 'image' not in self.jailspec:
            raise KeyError('Image not specified')
        im = Image.from_any_id(self.jailspec['image'], strict=True)
        self.jfs = JailFs.clone_from(im)
        jailspec = dict(self.jailspec)
        del jailspec['image']
        jailspec['path'] = self.jfs.path
        name = os.path.split(self.jfs.path)[-1]
        if 'name' not in jailspec:
            jailspec['name'] = name
        if 'host.hostname' not in jailspec:
            jailspec['host.hostname'] = name
        return JailSpec.from_dict(jailspec), self.jfs, self.jfs_take_ownership

    def __exit__(self, *_):
        if self.jfs is not None:
            self.jfs.destroy()
            self.jfs = None

    def jfs_take_ownership(self):
        jfs = self.jfs
        self.jfs = None
        return jfs


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


class one_exec_jailspec():
    def __init__(self, im: Image, jailspec: Dict = {}):
        if 'image' in jailspec:
            raise KeyError('image should be specified separately')

        self.im = im
        self.jailspec = jailspec

        self.jfs = None

    def __enter__(self):
        with ExitStack() as stack:
            jfs = JailFs.clone_from(self.im)
            stack.callback(jfs.destroy)
            jailspec = dict(self.jailspec)
            jailspec['path'] = jfs.path
            name = os.path.split(jfs.path)[-1]
            jailspec['name'] = 'one_' + name
            jailspec['host.hostname'] = name
            _ = stack.pop_all()
            self.jfs = jfs
            return JailSpec.from_dict(jailspec), jfs

    def __exit__(self, *_):
        self.jfs.destroy()
        self.jfs = None
