from focker.misc import merge_dicts
import pytest


class TestMergeDicts:
    def test01_different_types(self):
        with pytest.raises(TypeError, match='!='):
            _ = merge_dicts({}, [])

    def test02_delete(self):
        d = merge_dicts({ 'a': 1 }, { 'a': { '__delete__': True }})
        assert 'a' not in d

    def test03_delete_dict(self):
        d = merge_dicts({ 'a': { 'foo': 'bar', 'baf': 'baz' } },
            { 'a': { '__delete__': True }})
        assert 'a' not in d

    def test03_delete_nested(self):
        d = merge_dicts({ 'a': { 'foo': 'bar', 'baf': 'baz' } },
            { 'a': { 'foo': { '__delete__': True } }})
        assert 'a' in d
        assert 'foo' not in d['a']

    def test04_replace(self):
        d = merge_dicts({ 'a': { 'foo': 'bar', 'baf': 'baz' } },
            { 'a': { 'xyz': 'abc', 'def': 'upo', '__replace__': True } })
        assert 'a' in d
        assert d['a'] == { 'xyz': 'abc', 'def': 'upo' }
