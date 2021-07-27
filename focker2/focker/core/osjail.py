from .osjailspec import OSJailSpec
from .process import focker_subprocess_run, \
    focker_subprocess_check_output
from ..misc import load_jailconf

import shlex
import os
import json
from typing import Dict


OSJail = 'OSJail'


class OSJail:
    _init_key = object()
    def __init__(self, **kwargs):
        if kwargs.get('init_key') != OSJail._init_key:
            raise RuntimeError('OSJail must be created using one of the factory methods')

        self.name = kwargs['name']

    @classmethod
    def from_name(cls, name):
        conf = load_jailconf()
        for k, blk in conf.jail_blocks.items():
            if k == name:
                return OSJail(init_key=cls._init_key, name=name)
        raise RuntimeError('OSJail with the given name not found')

    @classmethod
    def from_mountpoint(cls, path):
        conf = load_jailconf()
        for k, blk in conf.jail_blocks.items():
            if blk['path'] == path:
                return OSJail(init_key=cls._init_key, name=k)
        raise RuntimeError('OSJail with the given mountpoint not found')

    def start(self):
        focker_subprocess_run([ 'jail', '-c', self.name ])

    def stop(self):
        focker_subprocess_run([ 'jail', '-r', self.name ])

    def run(self, cmd, *args, **kwargs):
        return focker_subprocess_run([ 'jexec', self.name, '/bin/sh', '-c', ' '.join([ shlex.quote(c) for c in cmd ]) ], *args, **kwargs)

    def check_output(self, cmd, *args, **kwargs):
        return focker_subprocess_check_output([ 'jexec', self.name, '/bin/sh', '-c', ' '.join([ shlex.quote(c) for c in cmd ]) ], *args, **kwargs)

    @property
    def jid(self):
        info = focker_subprocess_check_output([ 'jls', '--libxo',  'json', '-n' ])
        info = json.loads(info)
        info = [ j for j in info['jail-information']['jail']
            if j['name'] == self.name ]
        if len(info) == 0:
            return None
        if len(info) == 1:
            return int(info[0]['jid'])
        raise RuntimeError('Multiple jails with the same path - unsupported')


class TemporaryOSJail(OSJail):
    def __init__(self, spec, create_started=True, **kwargs):
        super().__init__(init_key=OSJail._init_key, name=None)

        self.spec = spec
        self.create_started = create_started

        self.ospec = None
        self.osjail = None

    def __enter__(self):
        self.ospec = OSJailSpec.from_jailspec(self.spec)
        self.ospec.add()
        self.name = self.ospec.name
        if self.create_started:
            self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.create_started:
            self.stop()
        self.ospec.remove()
