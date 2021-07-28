import pytest

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


    @pytest.mark.skip
    def test_create(self):
        pass

    @pytest.mark.skip
    def test_prune(self):
        pass

    @pytest.mark.skip
    def test_tag(self):
        pass

    @pytest.mark.skip
    def test_untag(self):
        pass

    @pytest.mark.skip
    def test_remove(self):
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
