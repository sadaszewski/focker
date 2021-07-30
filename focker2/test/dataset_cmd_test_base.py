import pytest
from focker.__main__ import main
from focker.core import zfs_exists, \
    zfs_destroy
from contextlib import redirect_stdout
from io import StringIO
import re


class DatasetCmdTestBase:
    _meta_class = None

    def test00_list_simple(self):
        cmd = [ self._meta_class._meta_focker_type, 'list' ]
        main(cmd)

    @pytest.mark.skip
    def test01_list_before_after_create(self):
        pass

    def test02_create(self):
        cmd = [ self._meta_class._meta_focker_type, 'create' ]
        buf = StringIO()
        with redirect_stdout(buf):
            main(cmd)
        m = re.findall('Created ([^ ]+) mounted at ([^ ]+)', buf.getvalue())
        assert len(m) == 1
        name = m[0][0]
        assert zfs_exists(name)
        zfs_destroy(name)

    @pytest.mark.skip
    def test03_prune(self):
        pass

    @pytest.mark.skip
    def test04_tag(self):
        pass

    @pytest.mark.skip
    def test05_untag(self):
        pass

    @pytest.mark.skip
    def test06_remove(self):
        pass

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
