#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


OSJailSpec = 'OSJailSpec'
import shlex
import os
from ..misc import load_jailconf, \
    save_jailconf
from ..jailconf import JailBlock
from .osjail.osjail import OSJail
from .mount import mount_from_spec


JailSpec = 'JailSpec'


def gen_env_command(command, env):
    if any(map(lambda a: ' ' in a, env.keys())):
        raise ValueError('Environment variable names cannot contain spaces')
    if not command:
        return ''
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

        self.params = kwargs['params']
        self.name = kwargs['name']

    @staticmethod
    def from_jailspec(jailspec: JailSpec) -> OSJailSpec:
        name = jailspec.name
        path = jailspec.path

        params = dict(jailspec.rest_params)

        prestart = []
        start = []
        poststop = []

        if jailspec.resolv_conf == 'system':
            prestart.append('cp /etc/resolv.conf ' +
                shlex.quote(os.path.join(path, 'etc/resolv.conf')))
        elif jailspec.resolv_conf == 'image':
            pass # leave as is
        elif 'file' in jailspec.resolv_conf:
            start.append(f'rm -vf /etc/resolv.conf && ln -s {shlex.quote(jailspec.resolv_conf["file"])} /etc/resolv.conf')
        elif 'system_file' in jailspec.resolv_conf:
            prestart.append(f'cp {shlex.quote(jailspec.resolv_conf["system_file"])} {shlex.quote(os.path.join(path, "etc/resolv.conf"))}')
        else:
            raise ValueError('Unsupported resolv_conf specification')

        for m in jailspec.mounts:
            m = mount_from_spec(m, path)

            source = m.source
            mountpoint = m.mountpoint

            prestart.append(f'mkdir -p {shlex.quote(mountpoint)}')
            prestart.append(f'mount -t {shlex.quote(m.fs_type)} {shlex.quote(source)} {shlex.quote(mountpoint)}')

            poststop.insert(0, f'umount -f {shlex.quote(mountpoint)}')

        exec_params = dict(jailspec.exec_params)
        exec_params['exec.prestart'] = prestart + exec_params.get('exec.prestart', [])
        exec_params['exec.start'] = start + exec_params.get('exec.start', []) + exec_params.get('command', [])
        if 'command' in exec_params:
            del exec_params['command']
        exec_params['exec.poststop'] = exec_params.get('exec.poststop', []) + poststop

        for k, v in exec_params.items():
            params[k] = gen_env_command(concat_commands(v), jailspec.env)

        params['path'] = path
        params['host.hostname'] = jailspec.hostname
        params['depend'] = [ OSJail.from_any_id(dep, strict=True).name for dep in jailspec.depend ]
        # mounts
        return OSJailSpec(init_key=OSJailSpec.__init_key, params=params, name=name)

    def to_dict(self):
        return dict(self.params)

    def to_jail_block(self):
        print('blk:', self.params)
        blk = JailBlock.create(self.name, self.params)
        return blk

    def add(self) -> OSJail:
        save_jailconf(self.params, jail_name=self.name)
        return OSJail.from_name(self.name)

    def remove(self):
        conf = load_jailconf(jail_name=self.name)
        os.unlink(os.path.join(conf['path'], '.ssman', 'jail_config.json'))

