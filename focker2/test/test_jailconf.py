import focker.jailconf as jc
from focker.jailconf.classes import *
import pytest


_TXT = """
a.b = 1;
a.c = ala;
a.d = "ala ma kota";
a.e = 5.5;
a.f = 1, 2, 3;
a.g = ab, cd, ef;
a.h = ab, 1, 2, cd, 3, 4, ef, 5, 6;
a.i = 1.5, 2.5, 3.5, a, b, c;
a.j = true;
a.k = false;

sameinjail {
    a.b = 1;
    a.c = ala;
    a.d = "ala ma kota";
    a.e = 5.5;
    a.f = 1, 2, 3;
    a.g = ab, cd, ef;
    a.h = ab, 1, 2, cd, 3, 4, ef, 5, 6;
    a.i = 1.5, 2.5, 3.5, a, b, c;
    a.j = true;
    a.k = false;
}
"""


_NATIVE = {
    'a.b': 1,
    'a.c': 'abc',
    'a.d': 1.5,
    'a.e': [1, 2, 3],
    'a.f': ['foo', 'bar', 'baf'],
    'a.g': [1.5, 2.5, 3.5],
    'a.h': [True, False, True, False],
    'a.i': True
}


class TestJailconf:
    def test01_read(self):
        _ = jc.loads(_TXT)

    def test02_dump(self):
        _ = jc.loads(_TXT)
        _ = str(_)

    def test03_dump_native_values(self):
        conf = jc.JailConf()
        conf['a.b'] = 1;
        conf['a.c'] = 'abc';
        conf['a.d'] = 1.5;
        conf['a.e'] = [1, 2, 3];
        conf['a.f'] = ['foo', 'bar', 'baf'];
        conf['a.g'] = [1.5, 2.5, 3.5];
        conf['a.h'] = [True, False, True, False];
        conf['a.i'] = True
        _ = str(conf)

    def test04_unexpected_type(self):
        conf = jc.JailConf()
        with pytest.raises(TypeError):
            conf['a.b'] = object()

    def test05_repr(self):
        conf = jc.loads(_TXT)
        _ = repr(conf)
        conf = jc.JailConf()
        conf.update(_NATIVE)
        _ = repr(conf)

    def test06_test_repr_simple(self):
        assert isinstance(repr(Value(5)), str)
        assert isinstance(repr(ListOfValues([ Value(3), Value(4) ])), str)
        assert isinstance(repr(KeyValuePair( [ Key('a.b'), '=', Value(5), ';' ] )), str)
        assert isinstance(repr(KeyValueAppendPair([ Key('a.b'), '+=', Value(5), ';' ])), str)
        assert isinstance(repr(KeyValueToggle([ Key('a.b'), ';' ])), str)
        assert isinstance(repr(Statements()), str)
        assert isinstance(repr(JailBlock.create('test')), str)
        assert isinstance(repr(JailConf()), str)

    def test07_append_append(self):
        conf = jc.JailConf()
        conf.append_append('a.b', True)
        conf.append_append('a.c', [ 1, 2, 3 ])
        assert '+=' in str(conf)

    def test08_getitem(self):
        lst = ListOfValues([ Value(3), Value(4), Value(5) ])
        _ = lst[0]
        with pytest.raises(IndexError):
            _ = lst[-1]
        with pytest.raises(IndexError):
            _ = lst[3]

    def test09_kvp(self):
        kvp = KeyValuePair([ Key('a.b'), '=', Value(5), ';' ])
        assert kvp.key == 'a.b'
        assert kvp.value == 5

    def test10_kvp_needskip(self):
        kvp = KeyValuePair([ Key('a.b'), '=', ListOfValues([]) ])
        assert str(kvp) == ''

    def test11_kvt(self):
        kvt = KeyValueToggle([ Key('a.nob'), ';' ])
        assert kvt.key == 'a.b'
        assert kvt.value == False
