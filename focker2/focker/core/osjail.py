from .jailspec import JailSpec
from .osjailspec import OSJailSpec, \
    gen_env_command
from .process import focker_subprocess_run, \
    focker_subprocess_check_output
from .image import Image
from ..misc import load_jailconf

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
            if k == name:
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
    def __init__(self, spec, create_started=True, **kwargs):
        self.spec = spec
        self.create_started = create_started

        self.ospec = None
        self.osjail = None

    def __enter__(self):
        self.ospec = OSJailSpec.from_jailspec(self.spec)
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
