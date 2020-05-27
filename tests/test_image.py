import pytest
from focker.image import validate_spec, \
    build_squeeze
import subprocess
from tempfile import TemporaryDirectory
import focker.image
import os
from focker.zfs import zfs_find, \
    zfs_mountpoint
from focker.misc import focker_unlock


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
