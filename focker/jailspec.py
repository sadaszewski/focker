import subprocess
import shlex
from .zfs import zfs_find, \
    zfs_mountpoint
import os
import jailconf
from .misc import focker_subprocess_check_output, \
    focker_subprocess_run


_params = focker_subprocess_check_output(['sysctl', '-N', 'security.jail.param'])
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


def quote(s):
    if isinstance(s, list):
        if len(s) == 0:
            return False
        elif len(s) == 1:
            return quote(s[0])
        else:
            return list(map(quote, s))
    if isinstance(s, bool):
        return s
    if isinstance(s, int):
        return str(s)
    if not isinstance(s, str):
        s = str(s)
    # if '\'' in s or '\\' in s or ' ' in s:
    s = s.replace('\\', '\\\\')
    s = s.replace('\'', '\\\'')
    s = '\'' + s + '\''
    return s


def gen_env_command(command, env):
    if any(map(lambda a: ' ' in a, env.keys())):
        raise ValueError('Environment variable names cannot contain spaces')
    env = [ 'export ' + k + '=' + shlex.quote(v) \
        for (k, v) in env.items() ]
    command = ' && '.join(env + [ command ])
    return command


def jailspec_to_jailconf(spec, name):
    for k in spec.keys():
        if k not in _params and k not in _focker_params:
            raise ValueError('Unknown parameter in jail spec: ' + k)

    if 'path' not in spec:
        raise ValueError('Missing path specification for the jail')

    path = spec['path']

    env = spec.get('env', {})

    mounts = spec.get('mounts', {})
    mounts = list(mounts.items())

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
        'host.hostname': name,
        'exec.start': '/bin/sh /etc/rc',
        'exec.stop': '/bin/sh /etc/rc.shutdown'
    }

    for k, v in spec.items():
        if k in _focker_params:
            continue
        if k in _exec_params:
            if isinstance(v, list):
                v = ' && '.join(v)
            # print('v:', v)
            v = gen_env_command(v, env)
        blk[k] = v

    prestart = [ 'cp /etc/resolv.conf ' +
        shlex.quote(os.path.join(path, 'etc/resolv.conf')) ]
    poststop = []
    if mounts:
        for from_, on in mounts:
            if not from_.startswith('/'):
                vol_name, *vol_path = from_.split('/')
                from_, _ = zfs_find(vol_name, focker_type='volume')
                from_ = zfs_mountpoint(from_)
                from_ = os.path.join(from_, *vol_path)
            prestart.append('mount -t nullfs ' + shlex.quote(from_) +
                ' ' + shlex.quote(os.path.join(path, on.strip('/'))))
        poststop += [ 'umount -f ' +
            os.path.join(path, on.strip('/')) \
            for (_, on) in reversed(mounts) ]

    if 'exec.prestart' in blk:
        prestart = prestart + [ blk['exec.prestart'] ]

    if 'exec.poststop' in blk:
        poststop = [ blk['exec.poststop'] ] + poststop

    prestart = ' && ' .join(prestart)
    poststop = ' && '.join(poststop)

    if prestart:
        blk['exec.prestart'] = prestart
    if poststop:
        blk['exec.poststop'] = poststop

    # print('blk:', blk)

    blk = {
        k: quote(v) for k, v in blk.items()
    }

    blk = { k: v for k, v in blk.items() \
        if not isinstance(v, bool) or v != False }

    # print('blk:', blk)

    blk = jailconf.JailBlock(blk)

    return blk
