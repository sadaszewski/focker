from focker.core import CacheBase
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
