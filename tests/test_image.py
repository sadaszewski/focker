import pytest
from focker.image import validate_spec, \
    build_squeeze, \
    build, \
    command_image_build, \
    command_image_tag, \
    command_image_untag, \
    command_image_list, \
    command_image_prune, \
    command_image_remove
import subprocess
from tempfile import TemporaryDirectory
import focker.image
import os
from focker.zfs import zfs_find, \
    zfs_mountpoint, \
    zfs_exists_snapshot_sha256, \
    zfs_parse_output, \
    zfs_exists
from focker.misc import focker_unlock
import yaml


def test_validate_spec_01():
    spec = { 'base': 'base', 'steps': 'steps' }
    validate_spec(spec)


def test_validate_spec_02():
    spec = { 'steps': 'steps' }
    with pytest.raises(ValueError):
        validate_spec(spec)


def test_validate_spec_03():
    spec = { 'base': 'base' }
    with pytest.raises(ValueError):
        validate_spec(spec)


def test_validate_spec_04():
    spec = {}
    with pytest.raises(ValueError):
        validate_spec(spec)


def test_build_squeeze(monkeypatch):
    focker_unlock()
    subprocess.check_output(['focker', 'image', 'remove', '--force', '-R', 'test-build-squeeze-base'])
    subprocess.check_output(['focker', 'bootstrap', '--dry-run', '-t', 'test-build-squeeze-base'])
    spec = dict(base='test-build-squeeze-base', steps=[
        dict(copy=['/etc/localtime', '/etc/localtime']),
        dict(copy=['/etc/hosts', '/etc/hosts'])
    ])
    _, base_sha256 = zfs_find('test-build-squeeze-base', focker_type='image')
    def fail(sha256, *args, **kwargs):
        if sha256 != base_sha256:
            raise RuntimeError('No pre-existing layers expected apart from base')
    monkeypatch.setattr(focker.image, 'zfs_snapshot_by_sha256', fail)
    with TemporaryDirectory() as d:
        args = lambda: 0
        args.focker_dir = d
        name, _ = build_squeeze(spec, args)
    focker_unlock()
    mountpoint = zfs_mountpoint(name.split('@')[0])
    print('name:', name, 'mountpoint:', mountpoint)
    assert os.path.exists(os.path.join(mountpoint, 'etc/localtime'))
    assert os.path.exists(os.path.join(mountpoint, 'etc/hosts'))
    subprocess.check_output(['focker', 'image', 'remove', '-R', 'test-build-squeeze-base'])
    assert not os.path.exists(mountpoint)


def test_build(monkeypatch):
    focker_unlock()
    subprocess.check_output(['focker', 'image', 'remove', '--force', '-R', 'test-build-squeeze-base'])
    subprocess.check_output(['focker', 'bootstrap', '--dry-run', '-t', 'test-build-squeeze-base'])
    spec = dict(base='test-build-squeeze-base', steps=[
        dict(copy=['/etc/localtime', '/etc/localtime']),
        dict(copy=['/etc/hosts', '/etc/hosts'])
    ])
    _, base_sha256 = zfs_find('test-build-squeeze-base', focker_type='image')

    counter = 0
    def count_calls(*args, **kwargs):
        nonlocal counter
        counter += 1
        return zfs_exists_snapshot_sha256(*args, **kwargs)
    monkeypatch.setattr(focker.image, 'zfs_exists_snapshot_sha256', count_calls)

    with TemporaryDirectory() as d:
        args = lambda: 0
        args.focker_dir = d
        name, _ = build(spec, args)

    assert counter == 2
    focker_unlock()
    mountpoint = zfs_mountpoint(name.split('@')[0])
    print('name:', name, 'mountpoint:', mountpoint)
    assert os.path.exists(os.path.join(mountpoint, 'etc/localtime'))
    assert os.path.exists(os.path.join(mountpoint, 'etc/hosts'))
    subprocess.check_output(['focker', 'image', 'remove', '-R', 'test-build-squeeze-base'])
    assert not os.path.exists(mountpoint)


def test_command_image_build():
    focker_unlock()
    subprocess.check_output(['focker', 'image', 'remove', '--force', '-R', 'test-command-image-build-base'])
    subprocess.check_output(['focker', 'bootstrap', '--dry-run', '-t', 'test-command-image-build-base'])

    with TemporaryDirectory() as d:
        args = lambda: 0
        with open(os.path.join(d, 'Fockerfile'), 'w') as f:
            yaml.dump(dict(base='test-command-image-build-base', steps=[
                dict(copy=['/etc/localtime', '/etc/localtime']),
                dict(copy=['/etc/hosts', '/etc/hosts'])
            ]), f)
        args.focker_dir = d
        args.squeeze = False
        args.tags = [ 'test-command-image-build' ]
        command_image_build(args)
        focker_unlock()

    name, _ = zfs_find('test-command-image-build', focker_type='image')
    mountpoint = zfs_mountpoint(name)
    assert os.path.exists(os.path.join(mountpoint, 'etc/localtime'))
    assert os.path.exists(os.path.join(mountpoint, 'etc/hosts'))

    subprocess.check_output(['focker', 'image', 'remove', '-R', 'test-command-image-build-base'])
    assert not os.path.exists(mountpoint)


def test_command_image_tag():
    focker_unlock()
    subprocess.check_output(['focker', 'image', 'remove', '--force', '-R', 'test-command-image-tag'])
    subprocess.check_output(['focker', 'bootstrap', '--dry-run', '-t', 'test-command-image-tag'])
    name_1, sha256_1 = zfs_find('test-command-image-tag', focker_type='image')
    args = lambda: 0
    args.reference = sha256_1
    args.tags = ['test-a', 'test-b', 'test-c']
    command_image_tag(args)
    for t in args.tags:
        name_2, sha256_2 = zfs_find(t, focker_type='image')
        assert name_2 == name_1
        assert sha256_2 == sha256_1
    subprocess.check_output(['focker', 'image', 'remove', '-R', 'test-command-image-tag'])
    for t in args.tags:
        with pytest.raises(ValueError):
            zfs_find(t, focker_type='image')
    with pytest.raises(ValueError):
        zfs_find('test-command-image-tag', focker_type='image')


def test_command_image_untag():
    focker_unlock()
    subprocess.check_output(['focker', 'image', 'remove', '--force', '-R', 'test-command-image-untag'])
    subprocess.check_output(['focker', 'bootstrap', '--dry-run', '-t', 'test-command-image-untag', 'test-command-image-untag-1', 'test-command-image-untag-2'])
    name, sha256 = zfs_find('test-command-image-untag', focker_type='image')
    args = lambda: 0
    args.tags = ['test-command-image-untag-1', 'test-command-image-untag-2']
    command_image_untag(args)
    tags = zfs_parse_output(['zfs', 'get', '-H', 'focker:tags', name])
    tags = tags[0][2].split(',')
    assert tags == ['test-command-image-untag']
    with pytest.raises(ValueError):
        zfs_find('test-command-image-untag-1', focker_type='image')
    with pytest.raises(ValueError):
        zfs_find('test-command-image-untag-2', focker_type='image')
    subprocess.check_output(['focker', 'image', 'remove', 'test-command-image-untag'])


def test_command_image_list(monkeypatch):
    focker_unlock()
    subprocess.check_output(['focker', 'image', 'remove', '--force', '-R', 'test-command-image-list'])
    subprocess.check_output(['focker', 'bootstrap', '--dry-run', '-t', 'test-command-image-list', 'test-command-image-list-1', 'test-command-image-list-2'])
    name, sha256 = zfs_find('test-command-image-list', focker_type='image')
    args = lambda: 0
    args.tagged_only = True
    args.full_sha256 = True
    lst = None
    headers = None
    def fake_tabulate(*args, **kwargs):
        nonlocal lst
        nonlocal headers
        lst = args[0]
        headers = kwargs['headers']
    monkeypatch.setattr(focker.image, 'tabulate', fake_tabulate)
    command_image_list(args)
    assert lst is not None
    assert headers == ['Tags', 'Size', 'SHA256', 'Base']
    assert len(lst) >= 3
    match = list(filter(lambda a: sorted(a[0].split(' ')) == ['test-command-image-list',  'test-command-image-list-1',  'test-command-image-list-2'], lst))
    assert len(match) == 1
    match = match[0]
    assert match[2] == sha256
    assert match[3] == '-'
    subprocess.check_output(['focker', 'image', 'remove', 'test-command-image-list'])


def test_command_image_prune():
    focker_unlock()
    subprocess.check_output(['focker', 'image', 'remove', '--force', '-R', 'test-command-image-prune'])
    subprocess.check_output(['focker', 'bootstrap', '--dry-run', '-t', 'test-command-image-prune'])
    name, sha256 = zfs_find('test-command-image-prune', focker_type='image')
    mountpoint = zfs_mountpoint(name)
    subprocess.check_output(['focker', 'image', 'untag', 'test-command-image-prune'])
    args = lambda: 0
    command_image_prune(args)
    with pytest.raises(ValueError):
        zfs_find('test-command-image-prune', focker_type='image')
    with pytest.raises(ValueError):
        zfs_find(sha256, focker_type='image')
    assert not os.path.exists(mountpoint)


def test_command_image_remove():
    focker_unlock()
    subprocess.check_output(['focker', 'image', 'remove', '--force', '-R', 'test-command-image-remove'])
    subprocess.check_output(['focker', 'bootstrap', '--dry-run', '-t', 'test-command-image-remove'])
    name, sha256 = zfs_find('test-command-image-remove', focker_type='image')
    mountpoint = zfs_mountpoint(name)
    args = lambda: 0
    args.reference = 'test-command-image-remove'
    args.force = False
    args.remove_dependents = False
    command_image_remove(args)
    with pytest.raises(ValueError):
        zfs_find('test-command-image-remove', focker_type='image')
    with pytest.raises(ValueError):
        zfs_find(sha256, focker_type='image')
    assert not os.path.exists(mountpoint)
    assert not zfs_exists(name)
