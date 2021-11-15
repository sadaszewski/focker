from focker.core import CacheBase, \
    JlsCache, \
    ZfsPropertyCache, \
    JailConfCache, \
    TemporaryOSJail, \
    clone_image_jailspec, \
    Volume, \
    Image
import pytest
from contextvars import ContextVar


class TestCacheBase:
    def test00_missing_context_var(self):
        cb = CacheBase()
        with pytest.raises(AttributeError):
            cb.__enter__()

    def test01_generate_cache_not_impl(self):
        cb = CacheBase()
        cb.context_var = ContextVar('FOCKER_UNIT_TEST_DUMMY', default=None)
        with pytest.raises(NotImplementedError):
            cb.__enter__()

    def test02_gen_cache(self):
        cb = CacheBase()
        cb.context_var = ContextVar('FOCKER_UNIT_TEST_DUMMY', default=None)
        cb.generate_cache = lambda: 0xdeadbeef
        with cb:
            assert cb.context_var.get() is not None
            assert cb.tok is not None
            assert cb.data == 0xdeadbeef
        assert cb.tok is None
        assert cb.context_var.get() is None

    def test03_is_available(self, monkeypatch):
        monkeypatch.setattr(CacheBase, 'context_var',
            ContextVar('FOCKER_UNIT_TEST_DUMMY', default=None))
        monkeypatch.setattr(CacheBase, 'generate_cache', lambda self: 0xdeadbeef)
        cb = CacheBase()
        with cb:
            assert CacheBase.is_available() == True
            assert CacheBase.instance() == cb
            with pytest.raises(NotImplementedError):
                _ = CacheBase.get_property('abc')

    def test04_no_cache_raise(self, monkeypatch):
        monkeypatch.setattr(CacheBase, 'context_var',
            ContextVar('FOCKER_UNIT_TEST_DUMMY', default=None))
        with pytest.raises(RuntimeError, match='No cache'):
            _ = CacheBase.get_property('abc')

    def test05_getitem(self):
        cb = CacheBase()
        cb.data = dict(foo='bar', bar='baf')
        assert 'foo' in cb
        assert 'bar' in cb
        assert cb['foo'] == 'bar'
        assert cb['bar'] == 'baf'
        assert cb.get('foo') == 'bar'
        assert cb.get('bar') == 'baf'
        assert cb.get('nonexistent') is None
        assert cb.get('nonexistent', default=0xdeadbeef) == 0xdeadbeef


class TestJlsCache:
    def test00_cache_after(self):
        with clone_image_jailspec(dict(image='freebsd-latest')) as (spec, jfs, *_), \
            TemporaryOSJail(spec) as oj, \
            JlsCache() as jc:

            assert JlsCache.is_available()
            assert JlsCache.instance() == jc
            assert oj.name in jc
            assert jc[oj.name]['name'] == oj.name
            assert jc[oj.name]['path'] == jfs.path

    def test01_cache_before(self):
        with JlsCache() as jc, \
            clone_image_jailspec(dict(image='freebsd-latest')) as (spec, *_), \
            TemporaryOSJail(spec) as oj:

            assert JlsCache.is_available()
            assert JlsCache.instance() == jc
            assert oj.name not in jc


class TestZfsPropertyCache:
    def test00_cache_after(self):
        with Volume.create() as v, \
            ZfsPropertyCache() as zc:

            assert ZfsPropertyCache.is_available()
            assert ZfsPropertyCache.instance() == zc
            assert v.name in zc
            assert zc[v.name]['mountpoint'] == v.mountpoint

    def test01_cache_before(self):
        with ZfsPropertyCache() as zc, \
            Volume.create() as v:

            assert ZfsPropertyCache.is_available()
            assert ZfsPropertyCache.instance() == zc
            assert v.name not in zc

    def test02_image_only(self):
        im = Image.from_tag('freebsd-latest')
        with Volume.create() as v, \
            ZfsPropertyCache(focker_type=['image']) as zc:

            assert ZfsPropertyCache.is_available()
            assert ZfsPropertyCache.instance() == zc
            assert v.name not in zc
            assert im.name in zc
            assert zc.get_property(im.name, 'mountpoint') == im.mountpoint


class TestJailConfCache:
    def test00_cache_after(self):
        assert not JailConfCache.is_available()
        with clone_image_jailspec(dict(image='freebsd-latest')) as (spec, jfs, *_), \
            TemporaryOSJail(spec, create_started=False) as oj, \
            JailConfCache() as jc:

            assert JailConfCache.is_available()
            assert JailConfCache.instance() == jc
            assert oj.name in jc.conf().jail_blocks
            # assert jc.conf().jail_blocks[oj.name]['name'] == oj.name
            assert jc.conf().jail_blocks[oj.name]['path'] == jfs.path

    def test01_cache_before(self):
        assert not JailConfCache.is_available()
        #with JailConfCache() as jc:
        #    print(str(jc.conf()))
        with JailConfCache() as jc:
            with clone_image_jailspec(dict(image='freebsd-latest')) as (spec, *_), \
                TemporaryOSJail(spec, create_started=False) as oj:

                assert JailConfCache.is_available()
                assert JailConfCache.instance() == jc
                # print(oj.name, jc.data.jail_blocks.keys())
                assert oj.name in jc.conf().jail_blocks
