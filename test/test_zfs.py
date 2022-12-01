from focker.core.zfs import *
import focker.core.zfs as zfs
import pytest
from focker.core import Volume
from contextlib import ExitStack


class TestZfs:
    def test01_create_existing(self):
        name = f'{zfs_poolname()}/focker-unit-test-zfs'
        zfs_create(name)
        assert zfs_exists(name)
        try:
            with pytest.raises(RuntimeError):
                zfs_create(name)
        finally:
            zfs_destroy(name)

    def test02_tag_spaces(self):
        name = f'{zfs_poolname()}/focker-unit-test-zfs'
        zfs_create(name)
        assert zfs_exists(name)
        try:
            with pytest.raises(ValueError):
                zfs_tag(name, ['tag with spaces'])
        finally:
            zfs_destroy(name)

    def test03_tag_minus(self):
        name = f'{zfs_poolname()}/focker-unit-test-zfs'
        zfs_create(name)
        assert zfs_exists(name)
        try:
            with pytest.raises(ValueError):
                zfs_tag(name, ['-'])
        finally:
            zfs_destroy(name)

    def test04_missing_poolname(self, monkeypatch):
        with monkeypatch.context() as c:
            c.setattr(zfs, 'zfs_parse_output', lambda *_: [])
            with pytest.raises(RuntimeError, match='not ZFS'):
                _ = zfs_poolname()

    def test05_untag_with_spaces(self):
        with pytest.raises(ValueError, match='spaces'):
            zfs_untag(['a tag with spaces'])

    def test06_destroy_protected(self):
        with ExitStack() as stack:
            v = Volume.create()
            stack.callback(lambda: v.unprotect() and v.destroy())
            v.protect()
            with pytest.raises(RuntimeError, match='protected'):
                zfs_destroy(v.name)
