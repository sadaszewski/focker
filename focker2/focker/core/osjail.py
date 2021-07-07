from .osjailspec import gen_env_command
import shlex
import os
from .mount import MountManager
from .process import focker_subprocess_check_output
from .misc import PrePostCommandManager
from typing import Dict
from .image import Image
from .jailspec import JailSpec
from .osjailspec import OSJailSpec


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
