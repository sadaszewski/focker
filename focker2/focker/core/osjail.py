from .jailspec import JailSpec
from .osjailspec import OSJailSpec, \
    gen_env_command
from .process import focker_subprocess_run, \
    focker_subprocess_check_output
from .image import Image
from .misc import get_path_and_name
from ..misc import load_jailconf, \
    jailconf_unquote

import shlex
import os
from typing import Dict


OSJail = 'OSJail'


class OSJail:
    __init_key = object()
    def __init__(self, **kwargs):
        if kwargs.get('init_key') != OSJail.__init_key:
            raise RuntimeError('OSJail must be created using one of the factory methods')

        self.name = kwargs['name']

    @classmethod
    def from_name(cls, name):
        conf = load_jailconf()
        for k, blk in conf.items():
            if jailconf_unquote(k) == name:
                return OSJail(init_key=cls.__init_key, name=name)
        raise RuntimeError('OSJail with the given name not found')

    def start(self):
        focker_subprocess_run([ 'jail', '-c', self.name ])

    def stop(self):
        focker_subprocess_run([ 'jail', '-r', self.name ])

    def run(self, cmd, *args, **kwargs):
        return focker_subprocess_run([ 'jexec', self.name, '/bin/sh', '-c', ' '.join([ shlex.quote(c) for c in cmd ]) ], *args, **kwargs)

    def check_output(self, cmd, *args, **kwargs):
        return focker_subprocess_check_output([ 'jexec', self.name, '/bin/sh', '-c', ' '.join([ shlex.quote(c) for c in cmd ]) ], *args, **kwargs)


class TemporaryOSJail:
    def __init__(self, mode='attach', use_rc=False, create_started=True, **kwargs):
        if mode != 'attach':
            raise RuntimeError('Temporary jail can only use "attach" mode')
        self.mode = mode
        self.use_rc = False
        self.create_started = create_started
        self.pathspec = { k: v for k, v in kwargs.items() if k in ['path', 'image', 'jailfs'] }

        self.ospec = None
        self.osjail = None

    def __enter__(self):
        path, name = get_path_and_name(self.pathspec, mode=self.mode)
        spec = { 'path': path, 'name': name }
        if not self.use_rc:
            spec.update({ 'exec.start': '', 'exec.stop': '' })
        spec = JailSpec.from_dict(spec)
        self.ospec = OSJailSpec.from_jailspec(spec)
        self.ospec.add()
        self.osjail = OSJail.from_name(self.ospec.name)
        if self.create_started:
            self.osjail.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.create_started:
            self.osjail.stop()
        self.ospec.remove()

    def __getattr__(self, attr):
        if hasattr(OSJail, attr):
            return getattr(self.osjail, attr)
        raise AttributeError
