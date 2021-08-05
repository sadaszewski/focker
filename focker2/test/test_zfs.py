from focker.core.zfs import *
import pytest


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
