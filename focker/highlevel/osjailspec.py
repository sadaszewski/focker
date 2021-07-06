OSJailSpec = 'OSJailSpec'
import shlex
from .jailspec import JailSpec
import os


def gen_env_command(command, env):
    if any(map(lambda a: ' ' in a, env.keys())):
        raise ValueError('Environment variable names cannot contain spaces')
    env = [ 'export ' + k + '=' + shlex.quote(v) \
        for (k, v) in env.items() ]
    command = ' && '.join(env + [ command ])
    return command


def concat_commands(lst):
    if isinstance(lst, str):
        return lst
    return ' && '.join(lst)


OSJailSpec = 'OSJailSpec'


class OSJailSpec:
    __init_key = object()

    def __init__(self, **kwargs):
        if kwargs.get('init_key') != OSJailSpec.__init_key:
            raise RuntimeError('OSJailSpec must be created using one of the factory methods')

        self.params = kwargs.get('params')

    @staticmethod
    def from_jailspec(jailspec: JailSpec) -> OSJailSpec:
        path = jailspec.image.path()

        params = dict(jailspec.rest_params)

        prestart = []
        poststop = []

        prestart.append('cp /etc/resolv.conf ' +
            shlex.quote(os.path.join(path, 'etc/resolv.conf')))

        for m in jailspec.mounts:
            source = m.source
            mountpoint = os.path.join(path, m.mountpoint.strip('/'))

            prestart.append(f'mount -t {shlex.quote(m.fs_type)} {shlex.quote(source)} {shlex.quote(mountpoint)}')

            poststop.insert(0, f'umount -f {shlex.quote(mountpoint)}')

        exec_params = dict(jailspec.exec_params)
        exec_params['exec.prestart'] = prestart + exec_params.get('exec.prestart', [])
        exec_params['exec.poststop'] = exec_params.get('exec.poststop', []) + poststop

        for k, v in exec_params.items():
            params[k] = gen_env_command(concat_commands(v), jailspec.env)

        params['path'] = path
        params['host.hostname'] = jailspec.hostname
        # mounts
        return OSJailSpec(init_key=OSJailSpec.__init_key, params=params)

    def to_dict(self):
        return dict(self.params)
