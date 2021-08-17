import pytest
import subprocess
from focker.volume import command_volume_create, \
    command_volume_prune, \
    command_volume_list, \
    command_volume_tag, \
    command_volume_untag, \
    command_volume_remove, \
    command_volume_set, \
    command_volume_get, \
    command_volume_protect, \
    command_volume_unprotect
from focker.zfs import zfs_find, \
    zfs_mountpoint, \
    zfs_exists, \
    zfs_parse_output, \
    zfs_destroy, \
    zfs_prune, \
    zfs_run
import os
import focker.volume
import focker.zfs


def test_command_volume_create():
    subprocess.check_output(['focker', 'volume', 'remove', '--force', 'test-command-volume-create'])
    args = lambda: 0
    args.tags = ['test-command-volume-create']
    command_volume_create(args)
    name, sha256 = zfs_find('test-command-volume-create', focker_type='volume')
    assert os.path.exists(zfs_mountpoint(name))
    subprocess.check_output(['focker', 'volume', 'remove', 'test-command-volume-create'])


def test_command_volume_prune():
    subprocess.check_output(['focker', 'volume', 'remove', '--force', 'test-command-volume-prune'])
    subprocess.check_output(['focker', 'volume', 'create', '-t', 'test-command-volume-prune'])
    name, sha256 = zfs_find('test-command-volume-prune', focker_type='volume')
    mountpoint = zfs_mountpoint(name)
    subprocess.check_output(['focker', 'volume', 'untag', 'test-command-volume-prune'])
    args = lambda: 0
    command_volume_prune(args)
    assert not zfs_exists(name)
    assert not os.path.exists(mountpoint)


def test_command_volume_list(monkeypatch):
    subprocess.check_output(['focker', 'volume', 'remove', '--force', 'test-command-volume-list'])
    subprocess.check_output(['focker', 'volume', 'create', '-t', 'test-command-volume-list', 'test-command-volume-list-1', 'test-command-volume-list-2'])
    name, sha256 = zfs_find('test-command-volume-list', focker_type='volume')
    mountpoint = zfs_mountpoint(name)
    args = lambda: 0
    args.full_sha256 = True
    lst = None
    headers = None
    def fake_tabulate(*args, **kwargs):
        nonlocal lst
        nonlocal headers
        lst = args[0]
        headers = kwargs['headers']
    monkeypatch.setattr(focker.volume, 'tabulate', fake_tabulate)
    command_volume_list(args)
    assert lst is not None
    assert headers == ['Tags', 'Size', 'SHA256', 'Mountpoint']
    assert len(lst) >= 3
    match = list(filter(lambda a: sorted(a[0].split(' ')) == ['test-command-volume-list',  'test-command-volume-list-1',  'test-command-volume-list-2'], lst))
    assert len(match) == 1
    match = match[0]
    assert match[2] == sha256
    assert match[3] == mountpoint
    subprocess.check_output(['focker', 'volume', 'remove', 'test-command-volume-list'])


def test_command_volume_tag():
    subprocess.check_output(['focker', 'volume', 'remove', '--force', 'test-command-volume-tag'])
    subprocess.check_output(['focker', 'volume', 'create', '-t', 'test-command-volume-tag'])
    name_1, sha256_1 = zfs_find('test-command-volume-tag', focker_type='volume')
    args = lambda: 0
    args.reference = sha256_1
    args.tags = ['test-a', 'test-b', 'test-c']
    command_volume_tag(args)
    for t in args.tags:
        name_2, sha256_2 = zfs_find(t, focker_type='volume')
        assert name_2 == name_1
        assert sha256_2 == sha256_1
    subprocess.check_output(['focker', 'volume', 'remove', 'test-command-volume-tag'])
    for t in args.tags:
        with pytest.raises(ValueError):
            zfs_find(t, focker_type='volume')
    with pytest.raises(ValueError):
        zfs_find('test-command-volume-tag', focker_type='volume')


def test_command_volume_untag():
    subprocess.check_output(['focker', 'volume', 'remove', '--force', 'test-command-volume-untag'])
    subprocess.check_output(['focker', 'volume', 'create', '-t', 'test-command-volume-untag', 'test-command-volume-untag-1', 'test-command-volume-untag-2'])
    name, sha256 = zfs_find('test-command-volume-untag', focker_type='volume')
    args = lambda: 0
    args.tags = ['test-command-volume-untag-1', 'test-command-volume-untag-2']
    command_volume_untag(args)
    tags = zfs_parse_output(['zfs', 'get', '-H', 'focker:tags', name])
    tags = tags[0][2].split(',')
    assert tags == ['test-command-volume-untag']
    with pytest.raises(ValueError):
        zfs_find('test-command-volume-untag-1', focker_type='volume')
    with pytest.raises(ValueError):
        zfs_find('test-command-image-untag-2', focker_type='volume')
    subprocess.check_output(['focker', 'volume', 'remove', 'test-command-volume-untag'])


def test_command_volume_remove():
    subprocess.check_output(['focker', 'volume', 'remove', '--force', 'test-command-volume-remove'])
    subprocess.check_output(['focker', 'volume', 'create', '-t', 'test-command-volume-remove'])
    name, sha256 = zfs_find('test-command-volume-remove', focker_type='volume')
    mountpoint = zfs_mountpoint(name)
    args = lambda: 0
    args.references = ['test-command-volume-remove']
    args.force = False
    command_volume_remove(args)
    with pytest.raises(ValueError):
        zfs_find('test-command-volume-remove', focker_type='volume')
    with pytest.raises(ValueError):
        zfs_find(sha256, focker_type='volume')
    assert not os.path.exists(mountpoint)
    assert not zfs_exists(name)


def test_command_volume_set():
    subprocess.check_output(['focker', 'volume', 'remove', '--force', 'test-command-volume-set'])
    subprocess.check_output(['focker', 'volume', 'create', '-t', 'test-command-volume-set'])
    name, sha256 = zfs_find('test-command-volume-set', focker_type='volume')
    args = lambda: 0
    args.reference = 'test-command-volume-set'
    args.properties = ['rdonly=on', 'quota=1G']
    command_volume_set(args)
    props = zfs_parse_output(['zfs', 'get', '-H', 'rdonly,quota', name])
    assert len(props) == 2
    for i in range(2):
        assert props[i][0] == name
    assert props[0][1] == 'readonly'
    assert props[1][1] == 'quota'
    assert props[0][2] == 'on'
    assert props[1][2] == '1G'
    subprocess.check_output(['focker', 'volume', 'remove', 'test-command-volume-set'])



def test_command_volume_get(monkeypatch):
    subprocess.check_output(['focker', 'volume', 'remove', '--force', 'test-command-volume-get'])
    subprocess.check_output(['focker', 'volume', 'create', '-t', 'test-command-volume-get'])
    subprocess.check_output(['focker', 'volume', 'set', 'test-command-volume-get', 'rdonly=on', 'quota=1G'])
    name, sha256 = zfs_find('test-command-volume-get', focker_type='volume')
    args = lambda: 0
    args.reference = 'test-command-volume-get'
    args.properties = ['rdonly', 'quota']
    lst = None
    headers = None
    def fake_tabulate(*args, **kwargs):
        nonlocal lst
        nonlocal headers
        lst = args[0]
        headers = kwargs['headers']
    monkeypatch.setattr(focker.volume, 'tabulate', fake_tabulate)
    command_volume_get(args)
    assert lst is not None
    assert headers is not None
    assert lst == [ ['rdonly', 'on'], ['quota', '1G'] ]
    assert headers == [ 'Property', 'Value' ]
    # assert lst == ['on', '1G']
    subprocess.check_output(['focker', 'volume', 'remove', 'test-command-volume-get'])


def test_command_volume_protect(monkeypatch):
    subprocess.check_output(['focker', 'volume', 'remove', '--force', 'test-command-volume-protect'])
    subprocess.check_output(['focker', 'volume', 'create', '-t', 'test-command-volume-protect'])
    args = lambda: 0
    args.references = ['test-command-volume-protect']
    command_volume_protect(args)
    name, sha256 = zfs_find('test-command-volume-protect', focker_type='volume')
    mountpoint = zfs_mountpoint(name)
    lst = zfs_parse_output(['zfs', 'get', '-H', 'focker:protect', name])
    assert len(lst) == 1
    assert lst[0][2] == 'on'
    with pytest.raises(RuntimeError):
        zfs_destroy(name)
    subprocess.check_output(['focker', 'volume', 'untag', 'test-command-volume-protect'])
    lst = zfs_parse_output(['zfs', 'get', '-H', 'focker:tags', name])
    assert len(lst) == 1
    assert lst[0][2] == '-'
    n_called = 0
    def fake_run(*args, **kwargs):
        nonlocal n_called
        n_called += 1
        return zfs_run(*args, **kwargs)
    monkeypatch.setattr(focker.zfs, 'zfs_run', fake_run)
    zfs_prune(focker_type='volume')
    assert not n_called == 1
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_output(['focker', 'volume', 'remove', sha256])
    subprocess.check_output(['zfs', 'destroy', '-r', '-f', name])
    assert not zfs_exists(name)
    assert not os.path.exists(mountpoint)


def test_command_volume_unprotect():
    subprocess.check_output(['focker', 'volume', 'remove', '--force', 'test-command-volume-unprotect'])
    subprocess.check_output(['focker', 'volume', 'create', '-t', 'test-command-volume-unprotect'])
    subprocess.check_output(['focker', 'volume', 'protect', 'test-command-volume-unprotect'])
    name, _ = zfs_find('test-command-volume-unprotect', focker_type='volume')
    lst = zfs_parse_output(['zfs', 'get', '-H', 'focker:protect', name])
    assert len(lst) == 1
    assert lst[0][2] == 'on'
    args = lambda: 0
    args.references = ['test-command-volume-unprotect']
    command_volume_unprotect(args)
    lst = zfs_parse_output(['zfs', 'get', '-H', 'focker:protect', name])
    assert len(lst) == 1
    assert lst[0][2] == '-'
    subprocess.check_output(['focker', 'volume', 'remove', 'test-command-volume-unprotect'])
