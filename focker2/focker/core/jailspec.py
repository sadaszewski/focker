from .image import Image
from typing import Dict
from .constant import JAIL_FOCKER_PARAMS, \
    JAIL_EXEC_PARAMS, \
    JAIL_PARAMS
from .mount import Mount
import os
from .jailfs import JailFs
import yaml
from ..misc import merge_dicts


DEFAULT_PARAMS = {
    'persist': True,
    'interface': 'lo1',
    'ip4.addr': '127.0.1.0',
    'mount.devfs': True,
    'exec.clean': True,
    'exec.start': '/bin/sh /etc/rc',
    'exec.stop': '/bin/sh /etc/rc.shutdown'
}


def load_default_jail_params_overrides():
    global DEFAULT_PARAMS
    for p in [ os.path.expanduser('~/.focker/jail-defaults.conf'),
        '/usr/local/etc/focker/jail-defaults.conf',
        '/etc/focker/jail-defaults.conf' ]:
        if os.path.exists(p):
            with open(p) as f:
                DEFAULT_PARAMS = merge_dicts(DEFAULT_PARAMS, yaml.safe_load(f))
            break


load_default_jail_params_overrides()


def ensure_list(lst):
    if not isinstance(lst, list):
        return [ lst ]
    return lst


class JailSpec:
    __init_key = object()

    def __init__(self, **kwargs) -> None:
        if kwargs.get('init_key') != JailSpec.__init_key:
            raise RuntimeError('JailSpec must be created using one of the factory methods')

        self.path = kwargs['path']
        self.hostname = kwargs['hostname']
        self.mounts = kwargs['mounts']
        self.env = kwargs['env']
        self.exec_params = kwargs['exec_params']
        self.rest_params = kwargs['rest_params']

    @staticmethod
    def validate_dict(jailspec: Dict):
        for k in jailspec.keys():
            if k not in JAIL_PARAMS and k not in JAIL_FOCKER_PARAMS:
                raise ValueError('Unknown parameter in jail spec: ' + k)

        if 'exec.start' in jailspec and 'command' in jailspec:
            raise KeyError('exec.start and command are mutually exclusive')

        if 'exec.jail_user' in jailspec and 'exec.system_jail_user' in jailspec:
            raise KeyError('exec.jail_user and exec.system_jail_user are mutually exclusive')

        if ('path' in jailspec) + ('image' in jailspec) + ('jailfs') != 1:
            raise RuntimeError('Exactly one of path, image or jailfs must be specified')

        if 'path' in jailspec and not os.path.exists(jailspec['path']):
            raise RuntimeError('Specified path does not exist')

    @staticmethod
    def from_dict(jailspec: Dict):
        JailSpec.validate_dict(jailspec)

        focker_spec = { k: v for k, v in jailspec.items()
            if k in JAIL_FOCKER_PARAMS }
        rest_spec_1 = { k: v for k, v in jailspec.items()
            if k not in JAIL_FOCKER_PARAMS }

        rest_spec = dict(DEFAULT_PARAMS)
        rest_spec.update(rest_spec_1)

        if 'path' in focker_spec:
            path = focker_spec['path']
        elif 'image' in focker_spec:
            path = Image.from_any_id(focker_spec['image'], strict=True)
            path = path.path()
        else:
            path = JailFs.from_any_id(focker_spec['jailfs'], strict=True)
            path = path.path()
        mounts = focker_spec.get('mounts', [])
        mounts = [ Mount(m[0], m[1]) for m in mounts ]
        env = focker_spec.get('env', {})
        hostname = rest_spec['host.hostname']

        del rest_spec['host.hostname']

        exec_params = { k: ensure_list(v) for k, v in rest_spec.items()
            if k in JAIL_EXEC_PARAMS }
        rest_params = { k: v for k, v in rest_spec.items()
            if k not in JAIL_EXEC_PARAMS }

        return JailSpec(init_key=JailSpec.__init_key, image=image,
            hostname=hostname, mounts=mounts, env=env,
            exec_params=exec_params, rest_params=rest_params)
