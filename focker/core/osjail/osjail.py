#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from ..process import focker_subprocess_run, \
    focker_subprocess_check_output, \
    CalledProcessError
from ...misc import focker_unlock
from ...misc.load_jailconf import *
import shlex
import os
import json
from typing import Dict
import subprocess
from ..cache import JlsCache
import tempfile
from ...jailconf import JailConf, \
    JailBlock


OSJail = 'OSJail'


class OSJail:
    _init_key = object()
    def __init__(self, **kwargs):
        if kwargs.get('init_key') != OSJail._init_key:
            raise RuntimeError('OSJail must be created using one of the factory methods')

        self.name = kwargs['name']

    @classmethod
    def from_name(cls, name):
        if not jailconf_jail_exists(name=name):
            raise RuntimeError('OSJail with the given name not found')
        return OSJail(init_key=cls._init_key, name=name)


    @classmethod
    def from_mountpoint(cls, path, raise_exc=True):
        conf = load_jailconf()
        for k, blk in conf.items():
            if 'path' in blk and blk['path'] == path:
                return OSJail(init_key=cls._init_key, name=k)
        if raise_exc:
            raise RuntimeError('OSJail with the given mountpoint not found')
        else:
            return None

    @classmethod
    def from_tag(cls, tag, raise_exc=True):
        from ..jailfs import JailFs
        jfs = JailFs.from_tag(tag, raise_exc=raise_exc)
        if jfs is not None:
            return cls.from_mountpoint(jfs.mountpoint, raise_exc=raise_exc)
        return None

    @classmethod
    def from_any_id(cls, reference, strict=True, raise_exc=True):
        from ..jailfs import JailFs
        jfs = JailFs.from_any_id(reference, strict=strict, raise_exc=raise_exc)
        if jfs is not None:
            return cls.from_mountpoint(jfs.mountpoint, raise_exc=raise_exc)
        return None

    @classmethod
    def from_sha256(cls, sha256, raise_exc=True):
        from ..jailfs import JailFs
        jfs = JailFs.from_sha256(sha256, raise_exc=raise_exc)
        if jfs is not None:
            return cls.from_mountpoint(jfs.mountpoint, raise_exc=raise_exc)
        return None

    def params_to_cmdline(self):
        cmd = []
        conf = jailconf_load_jail(name=self.name)
        cmd.append('name=' + self.name)
        for k, v in conf.items():
            if isinstance(v, list):
                if v:
                    cmd.append(f'{k}={",".join(v)}')
            elif isinstance(v, bool):
                if v:
                    cmd.append(k)
                else:
                    cmd.append(f'no{k}')
            else:
                cmd.append(f'{k}={v}')
        return cmd

    def start(self, **kwargs):
        jc = JailConf()
        for k, v in load_jailconf().items():
            jc[k] = JailBlock.create(k, v)
        cmd = [ 'jail', '-f', '-', '-c', self.name ]
        focker_subprocess_run(cmd, input=str(jc).encode('utf-8'), **kwargs)

    def stop(self, **kwargs):
        jc = JailConf()
        for k, v in load_jailconf().items():
            jc[k] = JailBlock.create(k, v)
        cmd = [ 'jail', '-f', '-', '-r', self.name ]
        focker_subprocess_run(cmd, input=str(jc).encode('utf-8'), **kwargs)

    def jexec(self, cmd, wrapper, *args, **kwargs):
        final_cmd = []
        fib = self.exec_fib
        if fib is not None:
            final_cmd.extend([ 'setfib', str(fib) ])
        final_cmd.extend([ 'jexec', self.name, '/bin/sh', '-c', ' '.join([ shlex.quote(c) for c in cmd ]) ])
        with focker_unlock():
            return wrapper(final_cmd, *args, **kwargs)

    def run(self, cmd, *args, **kwargs):
        return self.jexec(cmd, focker_subprocess_run, *args, **kwargs)

    def check_output(self, cmd, *args, **kwargs):
        return self.jexec(cmd, focker_subprocess_check_output, *args, **kwargs)

    @property
    def is_running(self):
        if JlsCache.is_available():
            return ( self.name in JlsCache.instance() )
        try:
            focker_subprocess_check_output([ 'jls', '-j', self.name ], stderr=subprocess.STDOUT)
        except CalledProcessError:
            return False
        return True

    def _jls(self):
        try:
            info = focker_subprocess_check_output([ 'jls', '--libxo',  'json', '-n', '-j', self.name ],
                stderr=subprocess.STDOUT)
        except CalledProcessError:
            raise RuntimeError('Not running')
        info = json.loads(info)
        info = [ j for j in info['jail-information']['jail']
            if j['name'] == self.name ]
        if len(info) == 0:
            raise RuntimeError('Not running') # pragma: no cover
        if len(info) == 1:
            return info[0]
        raise RuntimeError('Multiple jails with the same name - unsupported')

    def jls(self):
        if JlsCache.is_available():
            return JlsCache.instance()[self.name]
        return self._jls()

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
        blk = jailconf_load_jail(name=self.name)
        if 'exec.fib' in blk:
            return blk['exec.fib']
        else:
            return None

    def remove(self):
        if self.is_running:
            self.stop()
        jailconf_remove_jail(name=self.name)

    @property
    def conf(self):
        blk = jailconf_load_jail(name=self.name)
        return blk
