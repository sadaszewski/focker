from .image import Image
from typing import Dict
from ..jailspec import _focker_params, \
    _exec_params, \
    _params


DEFAULT_PARAMS = {
    'persist': True,
    'interface': 'lo1',
    'ip4.addr': '127.0.1.0',
    'mount.devfs': True,
    'exec.clean': True,
    'exec.start': '/bin/sh /etc/rc',
    'exec.stop': '/bin/sh /etc/rc.shutdown'
}


def ensure_list(lst):
    if not isinstance(lst, list):
        return [ lst ]
    return lst


class JailSpec:
    __init_key = object()

    def __init__(self, **kwargs) -> None:
        if kwargs.get('init_key') != JailSpec.__init_key:
            raise RuntimeError('JailSpec must be created using one of the factory methods')

        self.image = kwargs['image']
        self.hostname = kwargs['hostname']
        self.mounts = kwargs['mounts']
        self.env = kwargs['env']
        self.exec_params = kwargs['exec_params']
        self.rest_params = kwargs['rest_params']

    @staticmethod
    def from_jailspec_dict(jailspec: Dict):
        for k in jailspec.keys():
            if k not in _params and k not in _focker_params:
                raise ValueError('Unknown parameter in jail spec: ' + k)

        if 'exec.start' in jailspec and 'command' in jailspec:
            raise KeyError('exec.start and command are mutually exclusive')

        if 'exec.jail_user' in jailspec and 'exec.system_jail_user' in jailspec:
            raise KeyError('exec.jail_user and exec.system_jail_user are mutually exclusive')

        if 'path' in jailspec:
            raise RuntimeError('Path should not be specified, use image instead')

        focker_spec = { k: v for k, v in jailspec.items()
            if k in _focker_params }
        rest_spec_1 = { k: v for k, v in jailspec.items()
            if k not in _focker_params }

        rest_spec = dict(DEFAULT_PARAMS)
        rest_spec.update(rest_spec_1)

        #rest_spec = { k: v
        #    if k in _exec_params else v
        #    for k, v in rest_spec.items() }

        image = Image.from_any_id(focker_spec['image'], strict=True)
        mounts = focker_spec.get('mounts', [])
        env = focker_spec.get('env', {})
        hostname = rest_spec['host.hostname']

        del rest_spec['host.hostname']

        exec_params = { k: ensure_list(v) for k, v in rest_spec.items()
            if k in _exec_params }
        rest_params = { k: v for k, v in rest_spec.items()
            if k not in _exec_params }

        return JailSpec(init_key=JailSpec.__init_key, image=image,
            hostname=hostname, mounts=mounts, env=env,
            exec_params=exec_params, rest_params=rest_params)
