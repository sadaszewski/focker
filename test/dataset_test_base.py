import pytest
import os
from focker.core import zfs_exists, \
    zfs_set_props, \
    zfs_get_property, \
    zfs_destroy
from contextlib import ExitStack


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

    def test07_set(self):
        with ExitStack() as stack:
            ds = self._meta_class.create()
            stack.callback(ds.destroy)
            ds.set_props({ 'focker:foo': 'bar' })
            assert ds.get_props([ 'focker:foo' ])['focker:foo'] == 'bar'

    def test08_get(self):
        with ExitStack() as stack:
            ds = self._meta_class.create()
            stack.callback(ds.destroy)
            zfs_set_props(ds.name, { 'focker:foo': 'bar' })
            assert ds.get_props([ 'focker:foo' ])['focker:foo'] == 'bar'

    def test09_protect(self):
        with ExitStack() as stack:
            ds = self._meta_class.create()
            stack.callback(ds.destroy)
            ds.protect()
            stack.callback(ds.unprotect)
            val = zfs_get_property(ds.name, 'focker:protect')
            print(f'val: {val}.')
            assert val == 'on'

    def test10_unprotect(self):
        with ExitStack() as stack:
            ds = self._meta_class.create()
            stack.callback(ds.destroy)
            zfs_set_props(ds.name, { 'focker:protect': 'on' })
            ds.unprotect()
            assert zfs_get_property(ds.name, 'focker:protect') == '-'
