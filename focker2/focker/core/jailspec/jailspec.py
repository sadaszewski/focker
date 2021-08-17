#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from .constant import JAIL_FOCKER_PARAMS, \
    JAIL_EXEC_PARAMS, \
    JAIL_PARAMS
from ..mount import Mount
from ..misc import ensure_list
from ...misc import merge_dicts
from ..config import FOCKER_CONFIG
from typing import Dict
import os


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
        self.depend = ensure_list(kwargs['depend'])
        self.resolv_conf = kwargs['resolv_conf']

    @staticmethod
    def validate_dict(jailspec: Dict):
        for k in jailspec.keys():
            if k not in JAIL_PARAMS and k not in JAIL_FOCKER_PARAMS:
                raise KeyError('Unknown parameter in jail spec: ' + k)

        if 'exec.start' in jailspec and 'command' in jailspec:
            raise KeyError('exec.start and command are mutually exclusive')

        if 'exec.jail_user' in jailspec and 'exec.system_jail_user' in jailspec:
            raise KeyError('exec.jail_user and exec.system_jail_user are mutually exclusive')

        if 'path' not in jailspec:
            raise KeyError('Path not specified')

        if not os.path.exists(jailspec['path']):
            raise RuntimeError('Specified path does not exist')

        resolv_conf = jailspec.get('resolv_conf', 'system')
        if not resolv_conf == 'system' and \
            not resolv_conf == 'image' and \
                not ( isinstance(resolv_conf, dict) and \
                    ( 'file' in resolv_conf ) + \
                        ( 'system_file' in resolv_conf ) == 1 ):
            raise RuntimeError('Invalid resolv_conf specification')

    @classmethod
    def _from_dict(cls, jailspec: Dict):
        jailspec = merge_dicts(FOCKER_CONFIG.jail.default_params, jailspec)
        JailSpec.validate_dict(jailspec)

        focker_spec = { k: v for k, v in jailspec.items()
            if k in JAIL_FOCKER_PARAMS }
        rest_spec = { k: v for k, v in jailspec.items()
            if k not in JAIL_FOCKER_PARAMS }

        # rest_spec = dict(FOCKER_CONFIG.jail.default_params)
        # rest_spec.update(rest_spec_1)

        path = focker_spec['path']
        name = FOCKER_CONFIG.jail.name_prefix + focker_spec['name']
        hostname = focker_spec.get('host.hostname', name)
        depend = focker_spec.get('depend', [])

        mounts = focker_spec.get('mounts', {})
        mounts = [ Mount(k, v) for k, v in mounts.items() ]
        env = focker_spec.get('env', {})
        resolv_conf = focker_spec.get('resolv_conf', 'system')

        exec_params = { k: ensure_list(v) for k, v in rest_spec.items()
            if k in JAIL_EXEC_PARAMS }
        rest_params = { k: v for k, v in rest_spec.items()
            if k not in JAIL_EXEC_PARAMS }

        return cls(init_key=JailSpec._init_key, path=path,
            hostname=hostname, mounts=mounts, env=env,
            exec_params=exec_params, rest_params=rest_params,
            name=name, depend=depend, resolv_conf=resolv_conf)

    @classmethod
    def from_dict(cls, jailspec: Dict):
        return cls._from_dict(jailspec)
