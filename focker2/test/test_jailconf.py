import focker.jailconf as jc
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
