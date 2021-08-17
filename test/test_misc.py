from focker.misc.lock import focker_lock, \
    focker_unlock
from focker.misc import load_jailconf, \
    backup_file
from focker.jailconf import JailConf
from focker.jailconf.classes import Value
from focker.jailconf.misc import quote_value
from focker.command import materialize_parsers
import pytest
from argparse import ArgumentParser
import tempfile
import os


class TestMisc:
    def test01_focker_unlock_fd_none(self):
        if focker_lock.fd is not None:
            focker_lock.fd.close()
            focker_lock.fd = None
        assert focker_lock.fd is None
        with focker_unlock():
            pass
        assert focker_lock.fd is None

    def test02_load_jailconf_missing(self):
        res = load_jailconf('/this/file/surely/cannot/exist')
        assert isinstance(res, JailConf)

    def test03_backup_file_missing(self):
        res = backup_file('/this/file/surely/cannot/exist')
        assert res == (None, False)

    def test04_jailconf_quote_value_list(self):
        assert quote_value([]) is None
        assert quote_value([Value(1), Value(2)]) == '1,2'

    def test05_subp_and_func_both_raise(self):
        spec = dict(
            foo=dict(
                subparsers=dict(),
                func=lambda: 0
            )
        )
        parser = ArgumentParser()
        subp = parser.add_subparsers()
        with pytest.raises(KeyError, match='"subparsers" or "func"'):
            materialize_parsers(spec, subp, {})

    def test06_subp_override(self):
        spec = dict(
            foo=dict(
                func=lambda: 0,
                someparam=dict(
                    type=int,
                    default=123
                )
            )
        )
        parser = ArgumentParser()
        subp = parser.add_subparsers()
        materialize_parsers(spec, subp, { 'foo': { 'someparam': '456' } })
        cmd = [ 'foo' ]
        args = parser.parse_args(cmd)
        assert hasattr(args, 'someparam')
        assert args.someparam == 456

    def test07_backup_file(self):
        with tempfile.NamedTemporaryFile(mode='w') as f:
            f.write('foobar\n')
            f.flush()
            bak_fnam = f'{f.name}.bak'
            assert os.path.exists(f.name)
            assert backup_file(f.name) == (bak_fnam, True)
            print('bak_fnam:', bak_fnam)
            assert os.path.exists(bak_fnam)
            os.unlink(bak_fnam)

    def test08_nested_lock(self):
        with focker_lock():
            with pytest.raises(RuntimeError, match='expected to be None'):
                with focker_lock():
                    pass
