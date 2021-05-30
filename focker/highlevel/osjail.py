from ..jailspec import _params, \
    _focker_params, \
    _exec_params, \
    gen_env_command
import shlex
import os
from .mount import MountManager
from ..misc import focker_subprocess_check_output
from .misc import PrePostCommandManager
from typing import Dict
from .image import Image
from .jailspec import JailSpec

OSJailSpec = 'OSJailSpec'


class OSJailSpec:
    __init_key = object()

    def __init__(self, **kwargs):
        if kwargs.get('init_key') != OSJailSpec.__init_key:
            raise RuntimeError('OSJailSpec must be created using one of the factory methods')

        self.params = kwargs.get('params')

    @staticmethod
    def from_jailspec(jailspec: JailSpec) -> OSJailSpec:
        params = dict(jailspec.rest_params)
        params.update(jailspec.exec_params)
        params['path'] = jailspec.image.path()
        params['host.hostname'] = jailspec.hostname
        # mounts
        # env
        return OSJailSpec(init_key=OSJailSpec.__init_key, params=params)

    def to_dict(self):
        return dict(self.params)


OSJail = 'OSJail'


class OSJail:
    __init_key = object()
    def __init__(self, **kwargs):
        if kwargs.get('init_key') != OSJail.__init_key:
            raise RuntimeError('OSJail must be created using one of the factory methods')

        self.spec = kwargs['spec']

    def from_spec(spec: OSJailSpec) -> OSJail:
        return OSJail(spec=spec)
        
    def run_command(self, command):
        with (MountManager(self.mounts),
            PrePostCommandManager(' && '.join(self.prestart)),
                ' && '.join(self.poststop)):
            command = gen_env_command(command, self.env)
            focker_subprocess_check_output(command)

    def persist_to_jail_conf(self):
        pass
