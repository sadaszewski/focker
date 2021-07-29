import pytest
import os
from focker.core import zfs_exists


class DatasetTestBase:
    _meta_class = None

    def test00_list_simple(self):
        res = self._meta_class.list()
        assert isinstance(res, list)
        assert all(isinstance(elem, self._meta_class) for elem in res)

    def test01_list_before_after_create(self):
        res = self._meta_class.list()
        n = len(res)
        try:
            obj = self._meta_class.create()
            print(f'Created {obj.name} mounted at {obj.path}')
            res = self._meta_class.list()
            assert len(res) == n + 1
        finally:
            obj.destroy()

    def test02_create(self):
        ds = self._meta_class.create()
        try:
            assert os.path.exists(ds.path)
            assert zfs_exists(ds.name)
            assert self._meta_class.exists_sha256(ds.sha256)
        finally:
            ds.destroy()

    def test03_prune(self):
        ds = self._meta_class.create()
        name = ds.name
        try:
            assert zfs_exists(name)
            self._meta_class.prune()
            assert not zfs_exists(name)
        except:
            ds.destroy()
            raise

        t = 'focker-unit-test-dataset'
        ds = self._meta_class.create()
        try:
            assert zfs_exists(ds.name)
            ds.add_tags([ t ])
            self._meta_class.prune()
            assert zfs_exists(ds.name)
        finally:
            ds.destroy()

    def test04_tag(self):
        ds = self._meta_class.create()
        t = 'focker-unit-test-dataset'
        try:
            ds.add_tags([ t ])
            assert self._meta_class.exists_tag(t)
            assert self._meta_class.from_tag(t).sha256 == ds.sha256
        finally:
            ds.destroy()
        assert not self._meta_class.exists_tag(t)

    def test05_untag(self):
        ds = self._meta_class.create()
        t = 'focker-unit-test-dataset'
        try:
            ds.add_tags([ t ])
            assert self._meta_class.exists_tag(t)
            assert self._meta_class.from_tag(t).sha256 == ds.sha256
            ds.remove_tags([ t ])
            assert not self._meta_class.exists_tag(t)
        finally:
            ds.destroy()

    def test06_remove(self):
        ds = self._meta_class.create()
        try:
            assert os.path.exists(ds.path)
            assert zfs_exists(ds.name)
            sha256 = ds.sha256
            assert self._meta_class.exists_sha256(sha256)
        finally:
            ds.destroy()
        assert not self._meta_class.exists_sha256(sha256)

    @pytest.mark.skip
    def test_set(self):
        pass

    @pytest.mark.skip
    def test_get(self):
        pass

    @pytest.mark.skip
    def test_protect(self):
        pass

    @pytest.mark.skip
    def test_unprotect(self):
        pass
