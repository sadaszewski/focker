from focker.jail import backup_file, \
    jail_fs_create, \
    jail_create, \
    get_jid, \
    do_mounts, \
    undo_mounts, \
    jail_run, \
    jail_stop, \
    jail_remove, \
    command_jail_create, \
    command_jail_list
from focker.jailspec import gen_env_command, \
    quote
import tempfile
import os
import subprocess
from focker.zfs import zfs_mountpoint, \
    zfs_exists, \
    zfs_tag, \
    zfs_find
import jailconf
import shutil
from focker.mount import getmntinfo
import pytest
import focker.jail


def setup_module(module):
    subprocess.check_output(['focker', 'bootstrap', '--non-interactive', '--tags', 'test-jail'])


def teardown_module(module):
    subprocess.check_output(['focker', 'image', 'remove', 'test-jail'])


def test_backup_file():
    with tempfile.TemporaryDirectory() as d:
        fname = os.path.join(d, 'dummy.conf')
        with open(fname, 'w') as f:
            f.write('init')
        nbackups = 10
        for i in range(15):
            backup_file(fname, nbackups=nbackups, chmod=0o640)
            with open(fname, 'w') as f:
                f.write(str(i))

        fname = os.path.join(d, 'dummy.conf')
        with open(fname, 'r') as f:
            assert f.read() == '14'

        for i in range(nbackups):
            fname = os.path.join(d, 'dummy.conf.%d' % i)
            assert os.path.exists(fname)
            with open(fname, 'r') as f:
                if i < 5:
                    assert f.read() == str(i + 9)
                else:
                    assert f.read() == str(i - 1)


def test_jail_fs_create_01():
    subprocess.check_output(['focker', 'image', 'remove', '--force', '-R', 'test-jail-fs-create-01'])
    subprocess.check_output(['focker', 'bootstrap', '--empty', '-t', 'test-jail-fs-create-01'])
    name = jail_fs_create('test-jail-fs-create-01')
    assert zfs_exists(name)
    mountpoint = zfs_mountpoint(name)
    assert os.path.exists(mountpoint)
    with open(os.path.join(mountpoint, 'test.txt'), 'w') as f:
        f.write('test\n')
    assert os.path.exists(os.path.join(mountpoint, 'test.txt'))
    with open(os.path.join(mountpoint, 'test.txt'), 'r') as f:
        assert f.read() == 'test\n'
    subprocess.check_output(['focker', 'image', 'remove', '-R', 'test-jail-fs-create-01'])
    assert not zfs_exists(name)
    assert not os.path.exists(mountpoint)


def test_jail_fs_create_02():
    subprocess.check_output(['focker', 'jail', 'remove', '--force', 'test-jail-fs-create-02'])
    name = jail_fs_create()
    zfs_tag(name, ['test-jail-fs-create-02'])
    assert zfs_exists(name)
    mountpoint = zfs_mountpoint(name)
    assert os.path.exists(mountpoint)
    with open(os.path.join(mountpoint, 'test.txt'), 'w') as f:
        f.write('test\n')
    assert os.path.exists(os.path.join(mountpoint, 'test.txt'))
    with open(os.path.join(mountpoint, 'test.txt'), 'r') as f:
        assert f.read() == 'test\n'
    subprocess.check_output(['focker', 'jail', 'remove', 'test-jail-fs-create-02'])
    assert not zfs_exists(name)
    assert not os.path.exists(mountpoint)


def test_gen_env_command():
    command = gen_env_command('echo $TEST_VARIABLE_1 && echo $TEST_VARIABLE_2',
        {'TEST_VARIABLE_1': 'foo', 'TEST_VARIABLE_2': 'foo bar'})
    assert command == 'export TEST_VARIABLE_1=foo && export TEST_VARIABLE_2=\'foo bar\' && echo $TEST_VARIABLE_1 && echo $TEST_VARIABLE_2'


def test_quote():
    res = quote('foo \\ bar \'baz\'')
    assert res == '\'foo \\\\ bar \\\'baz\\\'\''


def test_jail_create():
    subprocess.check_output(['focker', 'jail', 'remove', '--force', 'test-jail-create'])
    subprocess.check_output(['focker', 'volume', 'remove', '--force', 'test-jail-create'])
    name = jail_fs_create()
    zfs_tag(name, ['test-jail-create'])
    subprocess.check_output(['focker', 'volume', 'create', '-t', 'test-jail-create'])
    mountpoint = zfs_mountpoint(name)

    spec = {
        'path': mountpoint,
        'exec.start': '/bin/sh /etc/rc',
        'env':  {
            'DUMMY_1': 'foo',
            'DUMMY_2': 'bar'
        },
        'mounts': {
            'test-jail-create': '/test-jail-create',
            '/tmp': '/test-tmp'
        },
        'ip4.addr': '127.1.2.3',
        'host.hostname': 'test-jail-create'
    }
    jail_name = os.path.split(mountpoint)[-1]
    jail_create(spec, jail_name)

    assert jail_name == os.path.split(mountpoint)[-1]
    assert os.path.exists(mountpoint)
    vol_name, _ = zfs_find('test-jail-create', focker_type='volume')
    vol_mountpoint = zfs_mountpoint(vol_name)
    assert os.path.exists(vol_mountpoint)
    conf = jailconf.load('/etc/jail.conf')
    assert jail_name in conf
    conf = conf[jail_name]
    assert conf['path'] == quote(mountpoint)
    assert conf['exec.start'] == '\'export DUMMY_1=foo && export DUMMY_2=bar && /bin/sh /etc/rc\''
    assert conf['exec.prestart'] == f'\'cp /etc/resolv.conf {mountpoint}/etc/resolv.conf && mount -t nullfs {vol_mountpoint} {mountpoint}/test-jail-create && mount -t nullfs /tmp {mountpoint}/test-tmp\''
    assert conf['ip4.addr'] == '\'127.1.2.3\''
    subprocess.check_output(['focker', 'jail', 'remove', 'test-jail-create'])
    subprocess.check_output(['focker', 'volume', 'remove', 'test-jail-create'])


def test_get_jid_01():
    subprocess.check_output(['focker', 'jail', 'create', 'test-jail', '--tags', 'test-get-jid-01', '--command', '/usr/bin/true'])
    name, _ = zfs_find('test-get-jid-01', focker_type='jail')
    mountpoint = zfs_mountpoint(name)
    subprocess.check_output(['focker', 'jail', 'start', 'test-get-jid-01'])
    _ = get_jid(mountpoint)
    subprocess.check_output(['focker', 'jail', 'remove', 'test-get-jid-01'])


def test_do_mounts_01():
    with tempfile.TemporaryDirectory() as d1:
        with tempfile.TemporaryDirectory() as d2:
            os.makedirs(os.path.join(d1, 'mnt'))
            os.makedirs(os.path.join(d2, 'test'))
            with open(os.path.join(d2, 'test', 'test.txt'), 'w') as f:
                f.write('Test\n')
            do_mounts(d1, [ (d2, '/mnt') ])
            assert os.path.exists(os.path.join(d1, 'mnt', 'test', 'test.txt'))
            with open(os.path.join(d1, 'mnt', 'test', 'test.txt'), 'r') as f:
                assert f.read() == 'Test\n'
            subprocess.check_output(['umount', '-f', os.path.join(d1, 'mnt')])


def test_undo_mounts_01():
    with tempfile.TemporaryDirectory() as d1:
        with tempfile.TemporaryDirectory() as d2:
            os.makedirs(os.path.join(d1, 'mnt'))
            subprocess.check_output([ 'mount', '-t', 'nullfs', d2,
                os.path.join(d1, 'mnt') ])
            print(getmntinfo())
            lst = [ a for a in getmntinfo() \
                if a['f_mntfromname'] == d2.encode('utf-8') ]
            assert len(lst) == 1
            undo_mounts(d1, [ (d2, '/mnt') ])
            lst = [ a for a in getmntinfo() \
                if a['f_mntfromname'] == d2.encode('utf-8') ]
            assert len(lst) == 0


def test_jail_run_01():
    subprocess.check_output(['focker', 'jail', 'create', 'test-jail', '--tags', 'test-jail-run-01'])
    name, _ = zfs_find('test-jail-run-01', focker_type='jail')
    mountpoint = zfs_mountpoint(name)
    jail_run(mountpoint, 'echo test-jail-run-01 >/tmp/test.txt')
    assert os.path.exists(os.path.join(mountpoint, 'tmp/test.txt'))
    with open(os.path.join(mountpoint, 'tmp/test.txt'), 'r') as f:
        assert f.read() == 'test-jail-run-01\n'
    subprocess.check_output(['focker', 'jail', 'remove', 'test-jail-run-01'])


def test_jail_stop_01():
    subprocess.check_output(['focker', 'jail', 'create', 'test-jail', '--tags', 'test-jail-stop-01'])
    name, _ = zfs_find('test-jail-stop-01', focker_type='jail')
    mountpoint = zfs_mountpoint(name)
    with pytest.raises(ValueError):
        _ = get_jid(mountpoint)
    subprocess.check_output(['focker', 'jail', 'start', 'test-jail-stop-01'])
    _ = get_jid(mountpoint)
    jail_stop(mountpoint)
    with pytest.raises(ValueError):
        _ = get_jid(mountpoint)
    subprocess.check_output(['focker', 'jail', 'remove', 'test-jail-stop-01'])


def test_jail_remove_01():
    subprocess.check_output(['focker', 'jail', 'create', 'test-jail', '--tags', 'test-jail-remove-01'])
    name, _ = zfs_find('test-jail-remove-01', focker_type='jail')
    mountpoint = zfs_mountpoint(name)
    with pytest.raises(ValueError):
        _ = get_jid(mountpoint)
    subprocess.check_output(['focker', 'jail', 'start', 'test-jail-remove-01'])
    _ = get_jid(mountpoint)
    jail_remove(mountpoint)
    with pytest.raises(ValueError):
        _ = get_jid(mountpoint)
    assert not os.path.exists(mountpoint)


def test_command_jail_create_01():
    args = lambda: 0
    args.image = 'test-jail'
    args.tags = [ 'test-command-jail-create-01' ]
    args.command = '/bin/sh /etc/rc'
    args.env = [ 'FOO:1', 'BAR:2' ]
    args.mounts = [ f'/no/path:/mnt' ]
    args.hostname = 'test-command-jail-create-01'
    command_jail_create(args)
    name, _ = zfs_find('test-command-jail-create-01', focker_type='jail')
    mountpoint = zfs_mountpoint(name)
    jail_sha256_prefix = name.split('/')[-1]
    conf = jailconf.load('/etc/jail.conf')
    assert jail_sha256_prefix in conf
    blk = conf[jail_sha256_prefix]
    assert blk['path'] == f'\'{mountpoint}\''
    assert blk['exec.start'] == f'\'export FOO=1 && export BAR=2 && {args.command}\''
    assert blk['exec.prestart'] == f'\'cp /etc/resolv.conf {mountpoint}/etc/resolv.conf && mount -t nullfs /no/path {mountpoint}/mnt\''
    assert blk['host.hostname'] == f'\'{args.hostname}\''
    subprocess.check_output(['focker', 'jail', 'remove', 'test-command-jail-create-01'])


def test_command_jail_list_01(monkeypatch):
    subprocess.check_output(['focker', 'jail', 'create', 'test-jail', '--tags', 'test-command-jail-list-01'])
    name, sha256 = zfs_find('test-command-jail-list-01', focker_type='jail')
    mountpoint = zfs_mountpoint(name)
    def fake_tabulate(data, headers):
        data = [ d for d in data \
            if d[0] == 'test-command-jail-list-01' ]
        assert len(data) == 1
        data = data[0]
        assert data[1] == sha256
        assert data[2] == mountpoint
        assert data[3] == '-'
        assert data[4] == 'test-jail'
    monkeypatch.setattr(focker.jail, 'tabulate', fake_tabulate)
    args = lambda: 0
    args.images = True
    args.full_sha256 = True
    command_jail_list(args)
    subprocess.check_output(['focker', 'jail', 'remove', 'test-command-jail-list-01'])
