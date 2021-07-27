from .osjailspec import OSJailSpec
from .process import focker_subprocess_run, \
    focker_subprocess_check_output, \
    CalledProcessError
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

    def jexec(self, cmd, wrapper, *args, **kwargs):
        final_cmd = []
        fib = self.exec_fib
        if fib is not None:
            final_cmd.extend([ 'setfib', str(fib) ])
        final_cmd.extend([ 'jexec', self.name, '/bin/sh', '-c', ' '.join([ shlex.quote(c) for c in cmd ]) ])
        return wrapper(final_cmd, *args, **kwargs)

    def run(self, cmd, *args, **kwargs):
        return self.jexec(cmd, focker_subprocess_run, *args, **kwargs)

    def check_output(self, cmd, *args, **kwargs):
        return self.jexec(cmd, focker_subprocess_check_output, *args, **kwargs)

    @property
    def is_running(self):
        try:
            focker_subprocess_check_output([ 'jls', '-j', self.name ])
        except subprocess.CalledProcessError:
            return False
        return True

    def jls(self):
        info = focker_subprocess_check_output([ 'jls', '--libxo',  'json', '-n' ])
        info = json.loads(info)
        info = [ j for j in info['jail-information']['jail']
            if j['name'] == self.name ]
        if len(info) == 0:
            raise RuntimeError('Not running')
        if len(info) == 1:
            return info[0]
        raise RuntimeError('Multiple jails with the same name - unsupported')

    def get_runtime_property(self, prop_name):
        info = self.jls()
        return info[prop_name]

    def has_runtime_property(self, prop_name):
        info = self.jls()
        return (prop_name in info)

    @property
    def jid(self):
        if not self.is_running:
            return None
        return int(self.get_runtime_property('jid'))

    @property
    def exec_fib(self):
        conf = load_jailconf()
        blk = conf[self.name]
        if 'exec.fib' in blk:
            return blk['exec.fib']
        else:
            return None


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
