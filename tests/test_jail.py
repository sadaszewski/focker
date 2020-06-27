from focker.jail import backup_file, \
    jail_fs_create, \
    jail_create, \
    get_jid, \
    do_mounts, \
    undo_mounts
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
    os.dup(1)
    with open('/dev/null', 'a') as devnull:
        os.dup2(devnull.fileno(), 3)
        subprocess.check_output(['focker', 'bootstrap', '--non-interactive', '--tags', 'test-get-jid-01'], stderr=subprocess.PIPE)
    # os.makedirs(os.path.join(mountpoint, 'usr/bin'))
    # os.makedirs(os.path.join(mountpoint, 'lib'))
    # os.makedirs(os.path.join(mountpoint, 'dev'))
    # os.makedirs(os.path.join(mountpoint, 'etc'))
    # shutil.copyfile('/etc/master.passwd', os.path.join(mountpoint, 'etc/master.passwd'))
    # shutil.copyfile('/usr/bin/true', os.path.join(mountpoint, 'usr/bin/true'))
    # shutil.copyfile('/lib/libc.so.7', os.path.join(mountpoint, 'lib/libc.so.7'))
    # subprocess.check_output(['zfs', 'set', 'rdonly=on', name])
    # subprocess.check_output(['zfs', 'snapshot', name + '@1'])
    subprocess.check_output(['focker', 'jail', 'create', 'test-get-jid-01', '--tags', 'test-get-jid-01', '--command', '/usr/bin/true'])
    name, _ = zfs_find('test-get-jid-01', focker_type='jail')
    mountpoint = zfs_mountpoint(name)
    subprocess.check_output(['focker', 'jail', 'start', 'test-get-jid-01'])
    _ = get_jid(mountpoint)
    subprocess.check_output(['focker', 'jail', 'remove', 'test-get-jid-01'])
    subprocess.check_output(['focker', 'image', 'remove', 'test-get-jid-01'])


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
