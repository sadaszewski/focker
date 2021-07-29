import pytest


class DatasetCmdTestBase:
    _meta_class = None

    @pytest.mark.skip
    def test00_list_simple(self):
        pass

    @pytest.mark.skip
    def test01_list_before_after_create(self):
        pass

    @pytest.mark.skip
    def test02_create(self):
        pass

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
