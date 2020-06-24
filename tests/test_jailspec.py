from focker.jailspec import jailspec_to_jailconf
import pytest


_spec = {
    'exec.prestart': 'echo Prestart',
    'exec.start': 'echo Start',
    'command': 'echo Command',
    'exec.poststart': 'echo Poststart',
    'exec.prestop': 'echo Prestop',
    'exec.stop': 'echo Stop',
    'exec.poststop': 'echo Poststop',
    'exec.clean': True,
    'exec.jail_user': 'nobody',
    'exec.system_jail_user': 'nobody',
    'exec.timeout': 60,
    'exec.consolelog': '/dev/null',
    'exec.fib': 'fib',
    'stop.timeout': 60,
    'interface': 'lo1',
    'ip4.addr': '127.0.1.0',
    'ip6.addr': 'abcd::',
    'vnet.interface': 'lo1',
    'ip_hostname': True,
    'mount': '/a /b nullfs',
    'mount.fstab': '/etc/fstab',
    'mount.fdescfs': True,
    'mount.procfs': True,
    'allow.dying': True,
    'depend': []
}


def test_jailspec_to_jailconf_01():
    with pytest.raises(KeyError) as excinfo:
        blk = jailspec_to_jailconf(_spec, {}, '/foo/bar', 'noname')
    assert excinfo.value.args == ('exec.start and command are mutually exclusive',)


def test_jailspec_to_jailconf_02():
    spec = dict(_spec)
    del spec['command']
    with pytest.raises(KeyError) as excinfo:
        blk = jailspec_to_jailconf(spec, {}, '/foo/bar', 'noname')
    assert excinfo.value.args == ('exec.jail_user and exec.system_jail_user are mutually exclusive',)


def test_jailspec_to_jailconf_03():
    spec = dict(_spec)
    del spec['command']
    del spec['exec.system_jail_user']
    #with pytest.raises(KeyError) as excinfo:
    blk = jailspec_to_jailconf(spec, {}, '/foo/bar', 'noname')
    # assert excinfo.value.args == ('exec.jail_user and exec.system_jail_user are mutually exclusive',)
