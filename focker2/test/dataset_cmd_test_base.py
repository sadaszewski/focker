import pytest
from focker.__main__ import main
from focker.core import zfs_exists, \
    zfs_destroy
from contextlib import redirect_stdout
from io import StringIO
import re


class DatasetCmdTestBase:
    _meta_class = None

    def _create(self):
        cmd = [ self._meta_class._meta_focker_type, 'create' ]
        buf = StringIO()
        with redirect_stdout(buf):
            main(cmd)
        m = re.findall('Created ([^ ]+) mounted at ([^ ]+)', buf.getvalue())
        assert len(m) == 1
        name = m[0][0]
        return name

    def test01_list_simple(self):
        cmd = [ self._meta_class._meta_focker_type, 'list' ]
        main(cmd)

    def test02_list_sort(self):
        cmd = [ self._meta_class._meta_focker_type, 'list', '-s', 'sha256' ]
        main(cmd)

    def test03_list_output(self):
        cmd = [ self._meta_class._meta_focker_type, 'list', '-o', 'is_protected' ]
        main(cmd)

    @pytest.mark.skip
    def test04_list_before_after_create(self):
        pass

    def test05_create(self):
        cmd = [ self._meta_class._meta_focker_type, 'create' ]
        buf = StringIO()
        with redirect_stdout(buf):
            main(cmd)
        m = re.findall('Created ([^ ]+) mounted at ([^ ]+)', buf.getvalue())
        assert len(m) == 1
        name = m[0][0]
        assert zfs_exists(name)
        zfs_destroy(name)

    def test06_prune(self):
        cmd = [ self._meta_class._meta_focker_type, 'create' ]
        buf = StringIO()
        with redirect_stdout(buf):
            main(cmd)
        m = re.findall('Created ([^ ]+) mounted at ([^ ]+)', buf.getvalue())
        assert len(m) == 1
        name = m[0][0]
        assert zfs_exists(name)
        cmd = [ self._meta_class._meta_focker_type, 'prune' ]
        main(cmd)
        assert not zfs_exists(name)

    def test07_tag(self):
        name = self._create()
        assert zfs_exists(name)
        ds = self._meta_class.from_name(name)
        try:
            cmd = [ self._meta_class._meta_focker_type, 'tag', ds.sha256, 'focker-unit-test-tag' ]
            main(cmd)
            assert 'focker-unit-test-tag' in ds.tags
        finally:
            ds.destroy()

    def test08_untag(self):
        name = self._create()
        ds = self._meta_class.from_name(name)
        ds.add_tags([ 'focker-unit-test-tag' ])
        try:
            cmd = [ self._meta_class._meta_focker_type, 'untag', ds.sha256, 'focker-unit-test-tag' ]
            main(cmd)
            assert 'focker-unit-test-tag' not in ds.tags
        finally:
            ds.destroy()

    def test09_remove(self):
        name = self._create()
        ds = self._meta_class.from_name(name)
        cmd = [ self._meta_class._meta_focker_type, 'remove', ds.sha256 ]
        main(cmd)
        assert not zfs_exists(name)

    def test10_set(self):
        name = self._create()
        ds = self._meta_class.from_name(name)
        try:
            cmd = [ self._meta_class._meta_focker_type, 'set', ds.sha256, 'quota=5G' ]
            main(cmd)
            assert ds.get_props([ 'quota' ])['quota'] == '5G'
        finally:
            ds.destroy()

    def test11_get(self):
        ds = self._meta_class.create()
        try:
            ds.set_props({ 'quota': '5G' })
            cmd = [ self._meta_class._meta_focker_type, 'get', ds.sha256, 'quota' ]
            buf = StringIO()
            with redirect_stdout(buf):
                main(cmd)
            buf = buf.getvalue().split('\n')
            buf = [ ln for ln in buf if 'quota' in ln and '5G' in ln ]
            assert len(buf) == 1
        finally:
            ds.destroy()

    @pytest.mark.skip
    def test_protect(self):
        pass

    @pytest.mark.skip
    def test_unprotect(self):
        pass
