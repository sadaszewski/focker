from focker.compose import exec_hook, \
    exec_prebuild, \
    exec_postbuild, \
    build_volumes, \
    build_images, \
    setup_dependencies, \
    build_jails, \
    stop_jails, \
    command_compose_build
import focker.compose
from tempfile import TemporaryDirectory
import os
import pytest
import fcntl
from focker.misc import focker_lock, \
    focker_unlock
import inspect
import ast
import stat
from focker.zfs import zfs_find, \
    zfs_mountpoint, \
    zfs_parse_output
import subprocess
import yaml
import jailconf
from focker.jail import backup_file
from collections import defaultdict


def test_exec_hook_01():
    spec = [
        'touch test-exec-hook-01',
        'touch test-exec-hook-02'
    ]
    with TemporaryDirectory() as d:
        exec_hook(spec, d, 'test-exec-hook')
        assert os.path.exists(os.path.join(d, 'test-exec-hook-01'))
        assert os.path.exists(os.path.join(d, 'test-exec-hook-02'))
    assert not os.path.exists(d)


def test_exec_hook_02():
    spec = 'touch test-exec-hook-01 && touch test-exec-hook-02'
    with TemporaryDirectory() as d:
        exec_hook(spec, d, 'test-exec-hook')
        assert os.path.exists(os.path.join(d, 'test-exec-hook-01'))
        assert os.path.exists(os.path.join(d, 'test-exec-hook-02'))
    assert not os.path.exists(d)


def test_exec_hook_03a():
    spec = 1
    with TemporaryDirectory() as d:
        with pytest.raises(ValueError):
            exec_hook(spec, d, 'test-exec-hook')


def test_exec_hook_03b():
    spec = [1]
    with TemporaryDirectory() as d:
        with pytest.raises(TypeError):
            exec_hook(spec, d, 'test-exec-hook')


def test_exec_hook_04():
    spec = 'ls'
    with pytest.raises(FileNotFoundError):
        exec_hook(spec, '/non-existent-directory/wcj20fy103', 'test-exec-hook')


def test_exec_hook_05():
    spec = 'ls'
    oldwd = os.getcwd()
    with TemporaryDirectory() as d:
        exec_hook(spec, d, 'test-exec-hook')
    assert os.getcwd() == oldwd


def test_exec_hook_06():
    spec = '/non-existent-command/hf249h'
    with TemporaryDirectory() as d:
        with pytest.raises(RuntimeError):
            exec_hook(spec, d, 'test-exec-hook')


def test_exec_hook_07():
    os.chdir('/')
    spec = 'flock --nonblock /var/lock/focker.lock -c ls'
    focker_lock()
    assert fcntl.flock(focker_lock.fd, fcntl.LOCK_EX | fcntl.LOCK_NB) != 0
    with TemporaryDirectory() as d:
        exec_hook(spec, d, 'test-exec-hook')
    assert fcntl.flock(focker_lock.fd, fcntl.LOCK_EX | fcntl.LOCK_NB) != 0
    focker_unlock()


def _test_simple_forward(fun, fwd_fun_name='exec_hook'):
    src = inspect.getsource(fun)
    mod = ast.parse(src)
    assert isinstance(mod.body[0], ast.FunctionDef)
    assert isinstance(mod.body[0].body[0], ast.Return)
    assert isinstance(mod.body[0].body[0].value, ast.Call)
    assert mod.body[0].body[0].value.func.id == fwd_fun_name


def test_exec_prebuild():
    _test_simple_forward(exec_prebuild)


def test_exec_postbuild():
    _test_simple_forward(exec_postbuild)


def test_build_volumes():
    subprocess.check_output(['focker', 'volume', 'remove', '--force', 'test-build-volumes'])
    err = False
    try:
        name, _ = zfs_find('test-build-volumes', focker_type='volume')
    except:
        err = True
    assert err
    spec = {
        'test-build-volumes': {
            'chown': '65534:65534',
            'chmod': 0o123,
            'protect': True,
            'zfs': {
                'quota': '1G',
                'readonly': 'on'
            }
        }
    }
    build_volumes(spec)
    name, _ = zfs_find('test-build-volumes', focker_type='volume')
    st = os.stat(zfs_mountpoint(name))
    assert st.st_uid == 65534
    assert st.st_gid == 65534
    assert ('%o' % st.st_mode)[-3:] == '123'
    zst = zfs_parse_output(['zfs', 'get', '-H', 'quota,readonly,focker:protect', name])
    assert zst[0][2] == '1G'
    assert zst[1][2] == 'on'
    assert zst[2][2] == 'on'
    subprocess.check_output(['zfs', 'destroy', '-r', '-f', name])


def test_build_images():
    subprocess.check_output(['focker', 'image', 'remove', '--force', 'test-focker-bootstrap'])
    subprocess.check_output(['focker', 'bootstrap', '--empty', '--tags', 'test-focker-bootstrap'])
    subprocess.check_output(['focker', 'image', 'remove', '--force', 'test-build-images'])
    with TemporaryDirectory() as d:
        with open(os.path.join(d, 'Fockerfile'), 'w') as f:
            yaml.dump({
                'base': 'test-focker-bootstrap',
                'steps': [
                    { 'copy': [
                        [ '/bin/sh', '/bin/sh', { 'chmod': 0o777 } ],
                        [ '/lib/libedit.so.7', '/lib/libedit.so.7' ],
                        [ '/lib/libncursesw.so.8', '/lib/libncursesw.so.8' ],
                        [ '/lib/libc.so.7', '/lib/libc.so.7' ],
                        [ '/usr/bin/touch', '/usr/bin/touch', { 'chmod': 0o777 } ],
                        [ '/libexec/ld-elf.so.1', '/libexec/ld-elf.so.1', { 'chmod': 0o555 } ]
                    ] },
                    { 'run': 'touch /test-build-images' }
                ]
            }, f)
        args = lambda: 0
        args.squeeze = False
        build_images({
            'test-build-images': '.'
        }, d, args)
    focker_unlock()
    name, _ = zfs_find('test-build-images', focker_type='image')
    assert os.path.exists(os.path.join(zfs_mountpoint(name), 'test-build-images'))
    subprocess.check_output(['focker', 'image', 'remove', '--force', 'test-build-images'])
    subprocess.check_output(['focker', 'image', 'prune'])
    subprocess.check_output(['focker', 'image', 'remove', '--force', 'test-focker-bootstrap'])


def test_setup_dependencies():
    backup_file('/etc/jail.conf')
    conf = jailconf.load('/etc/jail.conf')
    jail = jailconf.JailBlock()
    conf['test-setup-dependencies-A'] = jail
    conf['test-setup-dependencies-B'] = jail
    conf['test-setup-dependencies-C'] = jail
    conf.write('/etc/jail.conf')
    setup_dependencies({
        'test-setup-dependencies-A': {},
        'test-setup-dependencies-B': { 'depend': 'test-setup-dependencies-A' },
        'test-setup-dependencies-C': { 'depend': [
            'test-setup-dependencies-A',
            'test-setup-dependencies-B'
        ] }
    }, {
        'test-setup-dependencies-A': 'test-setup-dependencies-A',
        'test-setup-dependencies-B': 'test-setup-dependencies-B',
        'test-setup-dependencies-C': 'test-setup-dependencies-C'
    })
    conf = jailconf.load('/etc/jail.conf')
    assert 'depend' not in conf['test-setup-dependencies-A']
    assert conf['test-setup-dependencies-B']['depend'] == 'test-setup-dependencies-A'
    assert conf['test-setup-dependencies-C']['depend'] == [
        'test-setup-dependencies-A',
        'test-setup-dependencies-B'
    ]
    del conf['test-setup-dependencies-A']
    del conf['test-setup-dependencies-B']
    del conf['test-setup-dependencies-C']
    conf.write('/etc/jail.conf')


def test_build_jails():
    backup_file('/etc/jail.conf')
    conf = jailconf.load('/etc/jail.conf')
    for k in list(conf.keys()):
        if conf[k]['host.hostname'].strip('\'"') in ['test-build-jails-A', 'test-build-jails-B']:
            del conf[k]
    conf.write('/etc/jail.conf')
    subprocess.check_output(['focker', 'jail', 'remove', '--force', 'test-build-jails-A'])
    subprocess.check_output(['focker', 'jail', 'remove', '--force', 'test-build-jails-B'])
    subprocess.check_output(['focker', 'image', 'remove', '--force', '-R', 'test-focker-bootstrap'])
    subprocess.check_output(['focker', 'bootstrap', '--empty', '-t', 'test-focker-bootstrap'])
    spec = {
        'test-build-jails-A': {
            'image': 'test-focker-bootstrap',
            'exec.start': 'test-exec-start',
            'exec.stop': 'test-exec-stop',
            'ip4.addr': 'test-ip4-addr',
            'interface': 'test-interface',
            'host.hostname': 'test-build-jails-A',
            'allow.mount': True,
            'ip6.addr': 'abcd:abcd::0'
        }
    }
    spec['test-build-jails-B'] = spec['test-build-jails-A'].copy()
    spec['test-build-jails-B']['host.hostname'] = 'test-build-jails-B'
    build_jails(spec)
    conf = jailconf.load('/etc/jail.conf')
    print(conf.values())
    blocks = list(filter(lambda a: a['host.hostname'].strip('"\'') in [ 'test-build-jails-A',
        'test-build-jails-B' ], conf.values()))
    print(blocks)
    assert len(blocks) == 2
    assert blocks[0]['host.hostname'] != blocks[1]['host.hostname']
    for b in blocks:
        name, _ = zfs_find(b['host.hostname'].strip('\'"'), focker_type='jail')
        mountpoint = zfs_mountpoint(name)
        assert b['path'].strip('\'"') == mountpoint
        assert b['exec.start'].strip('\'"') == 'test-exec-start'
        assert b['exec.stop'].strip('\'"') == 'test-exec-stop'
        assert b['ip4.addr'].strip('\'"') == 'test-ip4-addr'
        assert b['interface'].strip('\'"') == 'test-interface'
        assert b['allow.mount']
        assert b['ip6.addr'] == '\'abcd:abcd::0\''
    subprocess.check_output(['focker', 'jail', 'remove', '--force', 'test-build-jails-A'])
    subprocess.check_output(['focker', 'jail', 'remove', '--force', 'test-build-jails-B'])
    subprocess.check_output(['focker', 'image', 'remove', '--force', 'test-focker-bootstrap'])
    for k in list(conf.keys()):
        if conf[k]['host.hostname'].strip('\'"') in ['test-build-jails-A', 'test-build-jails-B']:
            del conf[k]
    conf.write('/etc/jail.conf')


def test_stop_jails_01(monkeypatch):
    spec = {
        'foobar': {}
    }
    def mock_zfs_find(name, focker_type):
        assert name == 'foobar'
        assert focker_type == 'jail'
        return 'baf', None
    def mock_zfs_mountpoint(name):
        assert name == 'baf'
        return '/beef'
    def mock_jail_stop(path):
        assert path == '/beef'
    monkeypatch.setattr(focker.compose, 'zfs_find', mock_zfs_find)
    monkeypatch.setattr(focker.compose, 'zfs_mountpoint', mock_zfs_mountpoint)
    monkeypatch.setattr(focker.compose, 'jail_stop', mock_jail_stop)
    stop_jails(spec)


def test_stop_jails_02(monkeypatch):
    spec = {
        'foobar': {}
    }
    def mock_zfs_find(name, focker_type):
        assert name == 'foobar'
        assert focker_type == 'jail'
        raise ValueError('Not found')
    def mock_zfs_mountpoint(name):
        mock_zfs_mountpoint.called = True
    mock_zfs_mountpoint.called = False
    def mock_jail_stop(path):
        mock_jail_stop.called = True
    mock_jail_stop.called = False
    monkeypatch.setattr(focker.compose, 'zfs_find', mock_zfs_find)
    monkeypatch.setattr(focker.compose, 'zfs_mountpoint', mock_zfs_mountpoint)
    monkeypatch.setattr(focker.compose, 'jail_stop', mock_jail_stop)
    stop_jails(spec)
    assert not mock_zfs_mountpoint.called
    assert not mock_jail_stop.called


def test_command_compose_build(monkeypatch):
    with TemporaryDirectory() as d:
        with open(os.path.join(d, 'focker-compose.yml'), 'w') as f:
            yaml.dump({
                'exec.prebuild': 'echo exec-prebuild',
                'volumes': {},
                'images': {},
                'jails': {},
                'exec.postbuild': 'echo exec-postbuild'
            }, f)
        args = lambda: 0
        args.filename = os.path.join(d, 'focker-compose.yml')
        log = defaultdict(list)
        def log_calls(fun):
            old = fun.__call__
            def inner(*args, **kwargs):
                log[fun.__name__].append((args, kwargs))
                return old(*args, **kwargs)
            return inner

        monkeypatch.setattr(focker.compose, 'exec_prebuild', log_calls(exec_prebuild))
        monkeypatch.setattr(focker.compose, 'build_volumes', log_calls(build_volumes))
        monkeypatch.setattr(focker.compose, 'build_images', log_calls(build_images))
        monkeypatch.setattr(focker.compose, 'build_jails', log_calls(build_jails))
        monkeypatch.setattr(focker.compose, 'exec_postbuild', log_calls(exec_postbuild))
        command_compose_build(args)
        assert len(log) == 5
        assert 'exec_prebuild' in log
        assert 'build_volumes' in log
        assert 'build_images' in log
        assert 'build_jails' in log
        assert 'exec_postbuild' in log
        assert log['exec_prebuild'][0][0][0] == 'echo exec-prebuild'
        assert log['build_volumes'][0][0][0] == {}
        assert log['build_images'][0][0][0] == {}
        assert log['build_jails'][0][0][0] == {}
        assert log['exec_postbuild'][0][0][0] == 'echo exec-postbuild'
