import subprocess
from .jail import gen_env_command, \
    quote
import shlex
from .zfs import zfs_find, \
    zfs_mountpoint
import os


_params = subprocess.check_output(['sysctl', '-N', 'security.jail.param'])
_params = _params.decode('utf-8')
_params = _params.split('\n')
_params = filter(None, _params)
_params = { a[len('security.jail.param.'):].strip('.') \
    for a in _params }

_pseudo_params = {'exec.prestart', 'exec.start', 'command',
    'exec.poststart', 'exec.prestop', 'exec.stop', 'exec.poststop',
    'exec.clean', 'exec.jail_user', 'exec.system_jail_user',
    'exec.system_user', 'exec.timeout', 'exec.consolelog',
    'exec.fib', 'stop.timeout', 'interface', 'ip4.addr',
    'ip6.addr', 'vnet.interface', 'ip_hostname', 'mount',
    'mount.fstab', 'mount.fdescfs', 'mount.procfs', 'allow.dying',
    'depend'}

_params = _params.union(_pseudo_params)

_focker_params = { 'image', 'mounts', 'env' }

_exec_params = {'exec.prestart', 'exec.start', 'command',
    'exec.poststart', 'exec.prestop', 'exec.stop', 'exec.poststop'}

if _focker_params.intersection(_params):
    print('WARNING !!! Legal jail params collide with Focker params. Jail params will take precedence.')


def jailspec_to_jailconf(spec, env, path, name):
    if 'exec.start' in spec and 'command' in spec:
        raise KeyError('exec.start and command are mutually exclusive')

    if 'exec.jail_user' in spec and 'exec.system_jail_user' in spec:
        raise KeyError('exec.jail_user and exec.system_jail_user are mutually exclusive')

    blk = {
        'path': path,
        'persist': True,
        'interface': 'lo1',
        'ip4.addr': '127.0.1.0',
        'mount.devfs': True,
        'exec.clean': True,
        'host.hostname': name
    }

    for k, v in spec.items():
        if k not in _params and k not in _focker_params:
            raise ValueError('Unknown parameter in jail spec: ' + k)
        if k in _exec_params:
            if isinstance(v, list):
                v = ' && '.join(v)
            print('v:', v)
            v = gen_env_command(v, env)
        blk[k] = v

    prestart = [ 'cp /etc/resolv.conf ' +
        shlex.quote(os.path.join(path, 'etc/resolv.conf')) ]
    poststop = []
    mounts = spec.get('mounts', {})
    if mounts:
        for from_, on in mounts.items():
            if not from_.startswith('/'):
                from_, _ = zfs_find(from_, focker_type='volume')
                from_ = zfs_mountpoint(from_)
            prestart.append('mount -t nullfs ' + shlex.quote(from_) +
                ' ' + shlex.quote(os.path.join(path, on.strip('/'))))
        poststop += [ 'umount -f ' +
            os.path.join(path, on.strip('/')) \
            for (_, on) in reversed(mounts) ]

    prestart = ' && '.join(prestart)
    if 'exec.prestart' in blk:
        prestart = ' &&' .join([ prestart, blk['exec.prestart'] ])

    poststop = ' && '.join(poststop)
    if 'exec.poststop' in blk:
        poststop = ' && '.join([ blk['exec.poststop'], poststop ])

    if prestart:
        blk['exec.prestart'] = prestart
    if poststop:
        blk['exec.poststop'] = poststop

    # blk['path'] = path

    blk = {
        k: quote(v) if isinstance(v, str) else v \
            for k, v in blk.items()
    }

    # if command:
    #     command = gen_env_command(command, env)
    #     command = quote(command)
    #     print('command:', command)
    #     blk['exec.start'] = command


    # for (k, v) in overrides.items():
    #     blk[k] = quote(v) \
    #         if isinstance(v, str) \
    #         else v

    return blk
