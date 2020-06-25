import subprocess
from .jail import gen_env_command
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


def quote(s):
    if isinstance(s, list):
        return list(map(quote, s))
    if not isinstance(s, str):
        return s
    s = s.replace('\\', '\\\\')
    s = s.replace('\'', '\\\'')
    s = '\'' + s + '\''
    return s


def jailspec_to_jailconf(spec, name):
    for k in spec.keys():
        if k not in _params and k not in _focker_params:
            raise ValueError('Unknown parameter in jail spec: ' + k)

    if ('image' in spec) + ('path' in spec) != 1:
        raise ValueError('Either an image or a path must be specified for a jail')

    if 'image' in spec:
        path, _ = zfs_find(spec['image'], focker_type='image', zfs_type='snapshot')
        path = zfs_mountpoint(path)
    else:
        path = spec['path']

    env = spec['env'] if 'env' in spec else {}

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
    mounts = spec.get('mounts', {})
    mounts = list(mounts.items())
    if mounts:
        for from_, on in mounts:
            if not from_.startswith('/'):
                from_, _ = zfs_find(from_, focker_type='volume')
                from_ = zfs_mountpoint(from_)
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

    blk = {
        k: quote(v) for k, v in blk.items()
    }

    return blk
