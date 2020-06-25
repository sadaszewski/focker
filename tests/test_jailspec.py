from focker.jailspec import jailspec_to_jailconf, \
    quote
import pytest


_spec = {
    'path': '/no/path',
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


_spec2 = {
    'path': '/no/path',
    'sysvshm': 1,
    'sysvsem': 1,
    'sysvmsg': 1,
    'allow.mount.zfs': True,
    'allow.mount.tmpfs': True,
    'allow.mount.linsysfs': True,
    'allow.mount.linprocfs': True,
    'allow.mount.procfs': True,
    'allow.mount.nullfs': True,
    'allow.mount.fdescfs': True,
    'allow.mount.devfs': True,
    'allow.mount': True,
    'allow.socket_af': True,
    'allow.quotas': True,
    'allow.chflags': True,
    'allow.raw_sockets': True,
    'allow.sysvipc': True,
    'allow.set_hostname': True,
    'ip6.saddrsel': True,
    'ip6.addr': 'abcd::',
    'ip6': 'new',
    'ip4.saddrsel': True,
    'ip4.addr': '127.0.1.0',
    'ip4': 'new',
    'cpuset.id': 1,
    'host.hostid': 1,
    'host.hostuuid': 'abc-def',
    'host.domainname': 'a-domain-name',
    'host.hostname': 'a-host-name',
    'host': 'new',
    'children.max': 1,
    'children.cur': 0,
    'dying': False,
    'persist': True,
    'devfs_ruleset': 0,
    'enforce_statfs': True,
    'osrelease': '11.2',
    'osreldate': '2020-01-01',
    'securelevel': 1,
    'path': '/no/path',
    'name': 'no-name',
    'parent': 0,
    'jid': 1
}


def test_jailspec_to_jailconf_01():
    with pytest.raises(KeyError) as excinfo:
        blk = jailspec_to_jailconf(_spec, 'noname')
    assert excinfo.value.args == ('exec.start and command are mutually exclusive',)


def test_jailspec_to_jailconf_02():
    spec = dict(_spec)
    del spec['command']
    with pytest.raises(KeyError) as excinfo:
        blk = jailspec_to_jailconf(spec, 'noname')
    assert excinfo.value.args == ('exec.jail_user and exec.system_jail_user are mutually exclusive',)


def test_jailspec_to_jailconf_03():
    spec = dict(_spec)
    del spec['command']
    del spec['exec.system_jail_user']
    #with pytest.raises(KeyError) as excinfo:
    blk = jailspec_to_jailconf(spec, 'noname')
    # assert excinfo.value.args == ('exec.jail_user and exec.system_jail_user are mutually exclusive',)
    for k, v in spec.items():
        if k == 'exec.prestart' or k == 'exec.poststop':
            continue
        if isinstance(v, str):
            assert blk[k] == quote(v)
        else:
            assert blk[k] == v
    assert blk['exec.prestart'] == "'cp /etc/resolv.conf /no/path/etc/resolv.conf && echo Prestart'"
    assert blk['exec.poststop'] == "'echo Poststop'"


def test_jailspec_to_jailconf_04():
    spec = dict(_spec2)
    blk = jailspec_to_jailconf(spec, 'noname')
    for k, v in spec.items():
        if isinstance(v, str):
            assert blk[k] == quote(v)
        else:
            assert blk[k] == v


def test_jailspec_to_jailconf_05():
    spec = {
        'path': '/no/path',
        'env': {
            'FOO': 'bar',
            'BAR': 'baz'
        },
        'exec.prestart': 'echo Prestart',
        'exec.start': 'echo Start',
        'exec.poststart': 'echo Poststart',
        'exec.prestop': 'echo Prestop',
        'exec.stop': 'echo Stop',
        'exec.poststop': 'echo Poststop'
    }

    blk = jailspec_to_jailconf(spec, 'noname')

    assert blk['exec.prestart'] == "'cp /etc/resolv.conf /no/path/etc/resolv.conf && export FOO=bar && export BAR=baz && echo Prestart'"
    assert blk['exec.start'] == "'export FOO=bar && export BAR=baz && echo Start'"
    assert blk['exec.poststart'] == "'export FOO=bar && export BAR=baz && echo Poststart'"
    assert blk['exec.prestop'] == "'export FOO=bar && export BAR=baz && echo Prestop'"
    assert blk['exec.stop'] == "'export FOO=bar && export BAR=baz && echo Stop'"
    assert blk['exec.poststop'] == "'export FOO=bar && export BAR=baz && echo Poststop'"

    spec = {
        'path': '/no/path',
        'env': {
            'FOO': 'bar',
            'BAR': 'baz'
        },
        'command': 'echo Command'
    }

    blk = jailspec_to_jailconf(spec, 'noname')

    assert blk['command'] == "'export FOO=bar && export BAR=baz && echo Command'"


def test_jailspec_to_jailconf_06():
    with pytest.raises(ValueError) as excinfo:
        _ = jailspec_to_jailconf({}, 'noname')
    assert excinfo.value.args == ('Either an image or a path must be specified for a jail',)

    with pytest.raises(ValueError) as excinfo:
        _ = jailspec_to_jailconf({'image': 'zoo'}, 'noname')
    assert excinfo.value.args == ('Reference not found: zoo',)

    _ = jailspec_to_jailconf({'path': '/foo/bar'}, 'noname')

    with pytest.raises(ValueError) as excinfo:
        _ = jailspec_to_jailconf({'image': 'zoo', 'path': '/foo/bar'}, 'noname')
    assert excinfo.value.args == ('Either an image or a path must be specified for a jail',)


def test_jailspec_to_jailconf_07():
    spec = {
        'path': '/no/path',
        'mounts': {
            '/foo/bar': '/bar/baf',
            '/bar/baz': '/baz/bee'
        }
    }
    conf = jailspec_to_jailconf(spec, 'noname')

    assert conf['exec.prestart'] == quote('cp /etc/resolv.conf /no/path/etc/resolv.conf && mount -t nullfs /foo/bar /no/path/bar/baf && mount -t nullfs /bar/baz /no/path/baz/bee')

    assert conf['exec.poststop'] == quote('umount -f /no/path/baz/bee && umount -f /no/path/bar/baf')
