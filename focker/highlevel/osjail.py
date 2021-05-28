from ..jailspec import _params, \
    _focker_params, \
    _exec_params, \
    gen_env_command
import shlex
import os
from .mount import MountManager
from ..misc import focker_subprocess_check_output
from .misc import PrePostCommandManager


DEFAULT_PARAMS = {
    'persist': True,
    'interface': 'lo1',
    'ip4.addr': '127.0.1.0',
    'mount.devfs': True,
    'exec.clean': True,
    'exec.start': '/bin/sh /etc/rc',
    'exec.stop': '/bin/sh /etc/rc.shutdown'
}


class OSJailParams:
    def __init__(self, path, hostname, params):
        self.params = dict(DEFAULT_PARAMS)
        self.params.update(params)
        self.params['path'] = path
        self.params['host.hostname'] = hostname

    def to_dict(self):
        return dict(self.params)


class OSJail:
    def __init__(self, image, mounts, env, params: OSJailParams):
        self.image = image
        self.mounts = mounts
        self.env = env
        self.params = params

        self.prestart = [ 'cp /etc/resolv.conf ' +
            shlex.quote(os.path.join(path, 'etc/resolv.conf')) ]
        self.poststop = []

    def run_command(self, command):
        with MountManager(self.mounts),
            PrePostCommandManager(' && '.join(self.prestart),
                ' && '.join(self.poststop)):
            command = gen_env_command(command, self.env)
            focker_subprocess_check_output(command)

    def persist_to_jail_conf(self):
        pass
