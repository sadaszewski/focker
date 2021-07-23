from .image import Image
from .constant import JAIL_FOCKER_PARAMS, \
    JAIL_EXEC_PARAMS, \
    JAIL_PARAMS
from .mount import Mount
from .jailfs import JailFs
from ..misc import merge_dicts, \
    load_overrides

from typing import Dict
import os
import ruamel.yaml as yaml
import hashlib


DEFAULT_PARAMS = {
    'persist': True,
    'interface': 'lo1',
    'ip4.addr': '127.0.1.0',
    'mount.devfs': True,
    'exec.clean': True,
    'exec.start': '/bin/sh /etc/rc',
    'exec.stop': '/bin/sh /etc/rc.shutdown'
}


JAIL_NAME_PREFIX = 'focker_'


def load_default_jail_param_overrides():
    global DEFAULT_PARAMS
    ovr = load_overrides('jail-defaults.conf')
    DEFAULT_PARAMS = merge_dicts(DEFAULT_PARAMS, ovr)

load_default_jail_param_overrides()


def load_jail_name_prefix_override():
    global JAIL_NAME_PREFIX
    ovr = load_overrides('focker.conf', [ 'jail_name_prefix' ])
    JAIL_NAME_PREFIX = ovr.get('jail_name_prefix', JAIL_NAME_PREFIX)

load_jail_name_prefix_override()


def ensure_list(lst):
    if not isinstance(lst, list):
        return [ lst ]
    return lst


class JailSpec:
    _init_key = object()

    def __init__(self, **kwargs) -> None:
        if kwargs.get('init_key') != JailSpec._init_key:
            raise RuntimeError(f'{self.__class__.__name__} must be created using one of the factory methods')

        self.path = kwargs['path']
        self.hostname = kwargs['hostname']
        self.mounts = kwargs['mounts']
        self.env = kwargs['env']
        self.exec_params = kwargs['exec_params']
        self.rest_params = kwargs['rest_params']
        self.name = kwargs['name']

    @staticmethod
    def validate_dict(jailspec: Dict):
        for k in jailspec.keys():
            if k not in JAIL_PARAMS and k not in JAIL_FOCKER_PARAMS:
                raise ValueError('Unknown parameter in jail spec: ' + k)

        if 'exec.start' in jailspec and 'command' in jailspec:
            raise KeyError('exec.start and command are mutually exclusive')

        if 'exec.jail_user' in jailspec and 'exec.system_jail_user' in jailspec:
            raise KeyError('exec.jail_user and exec.system_jail_user are mutually exclusive')

        if 'path' not in jailspec:
            raise RuntimeError('Path not specified')

        if not os.path.exists(jailspec['path']):
            raise RuntimeError('Specified path does not exist')

    @classmethod
    def _from_dict(cls, jailspec: Dict):
        JailSpec.validate_dict(jailspec)

        focker_spec = { k: v for k, v in jailspec.items()
            if k in JAIL_FOCKER_PARAMS }
        rest_spec_1 = { k: v for k, v in jailspec.items()
            if k not in JAIL_FOCKER_PARAMS }

        rest_spec = dict(DEFAULT_PARAMS)
        rest_spec.update(rest_spec_1)

        path = focker_spec['path']
        name = JAIL_NAME_PREFIX + focker_spec['name']
        hostname = focker_spec.get('host.hostname', name)

        mounts = focker_spec.get('mounts', [])
        mounts = [ Mount(m[0], m[1]) for m in mounts ]
        env = focker_spec.get('env', {})

        exec_params = { k: ensure_list(v) for k, v in rest_spec.items()
            if k in JAIL_EXEC_PARAMS }
        rest_params = { k: v for k, v in rest_spec.items()
            if k not in JAIL_EXEC_PARAMS }

        return cls(init_key=JailSpec._init_key, path=path,
            hostname=hostname, mounts=mounts, env=env,
            exec_params=exec_params, rest_params=rest_params,
            name=name)

    @classmethod
    def from_dict(cls, jailspec: Dict):
        return cls._from_dict(jailspec)


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
