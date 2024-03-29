#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from ..process import focker_subprocess_check_output


def get_jail_sysctl_params():
    _params = focker_subprocess_check_output(['sysctl', '-N', 'security.jail.param'])
    _params = _params.decode('utf-8')
    _params = _params.split('\n')
    _params = filter(None, _params)
    _params = { a[len('security.jail.param.'):].strip('.') \
        for a in _params }
    _params.remove('path')
    _params.remove('name')
    _params.remove('host.hostname')
    return _params


JAIL_SYSCTL_PARAMS = get_jail_sysctl_params()


JAIL_PSEUDO_PARAMS = {'exec.prestart', 'exec.start', 'command',
    'exec.poststart', 'exec.prestop', 'exec.stop', 'exec.poststop',
    'exec.clean', 'exec.jail_user', 'exec.system_jail_user',
    'exec.system_user', 'exec.timeout', 'exec.consolelog',
    'exec.fib', 'stop.timeout', 'interface', 'ip4.addr',
    'ip6.addr', 'vnet.interface', 'ip_hostname', 'mount',
    'mount.fstab', 'mount.devfs', 'mount.fdescfs', 'mount.procfs',
    'allow.dying'}


JAIL_PARAMS = JAIL_SYSCTL_PARAMS.union(JAIL_PSEUDO_PARAMS)


JAIL_FOCKER_PARAMS = { 'image', 'mounts', 'env', 'jailfs', 'path',
    'name', 'host.hostname', 'depend', 'resolv_conf', 'meta' }


JAIL_EXEC_PARAMS = {'exec.prestart', 'exec.start', 'command',
    'exec.poststart', 'exec.prestop', 'exec.stop', 'exec.poststop'}


if JAIL_FOCKER_PARAMS.intersection(JAIL_PARAMS):
    print('WARNING !!! Legal jail params collide with Focker params. Jail params will take precedence.') # pragma: no cover
