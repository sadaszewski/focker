from ..constant import JAIL_FOCKER_PARAMS, \
    JAIL_EXEC_PARAMS, \
    JAIL_PARAMS
from ..mount import Mount
from ..misc import ensure_list
from .constant import DEFAULT_PARAMS, \
    JAIL_NAME_PREFIX
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
        depend = focker_spec.get('depend', [])

        mounts = focker_spec.get('mounts', {})
        mounts = [ Mount(k, v) for k, v in mounts.items() ]
        env = focker_spec.get('env', {})

        exec_params = { k: ensure_list(v) for k, v in rest_spec.items()
            if k in JAIL_EXEC_PARAMS }
        rest_params = { k: v for k, v in rest_spec.items()
            if k not in JAIL_EXEC_PARAMS }

        return cls(init_key=JailSpec._init_key, path=path,
            hostname=hostname, mounts=mounts, env=env,
            exec_params=exec_params, rest_params=rest_params,
            name=name, depend=depend)

    @classmethod
    def from_dict(cls, jailspec: Dict):
        return cls._from_dict(jailspec)
