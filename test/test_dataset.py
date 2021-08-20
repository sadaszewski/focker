from focker.core import Image, \
    Volume, \
    zfs_destroy, \
    zfs_exists, \
    zfs_get_property, \
    zfs_set_props
import pytest
from contextlib import ExitStack


class TestDataset:
    def test01_ctor_methods(self):
        with pytest.raises(RuntimeError):
            im = Image()

    def test02_no_cloning(self):
        v = Volume.create()
        try:
            with pytest.raises(RuntimeError):
                _ = Volume.clone_from(v)
        finally:
            v.destroy()

    def test03_clone_wrong_type(self):
        v = Volume.create()
        try:
            with pytest.raises(TypeError):
                _ = Image.clone_from(v)
        finally:
            v.destroy()

    def test04_not_finalized(self):
        im = Image.create()
        try:
            with pytest.raises(RuntimeError):
                _ = Image.clone_from(im)
        finally:
            im.destroy()

    def test05_sha256_clash(self):
        im = Image.create(sha256='1234567xxx')
        try:
            with pytest.raises(RuntimeError, match='already exists'):
                im = Image.create(sha256='1234567xxx')
        finally:
            im.destroy()

    def test06_cant_finalize(self):
        v = Volume.create()
        try:
            with pytest.raises(RuntimeError):
                v.finalize()
        finally:
            v.destroy()

    def test07_not_found(self):
        with pytest.raises(RuntimeError, match='not found'):
            _ = Image.from_any_id('focker-unit-test-impossible-id')

    def test08_ambiguous(self):
        with ExitStack() as stack:
            v_1 = Volume.create(sha256='1234567x')
            stack.callback(v_1.destroy)
            v_2 = Volume.create(sha256='1234567y')
            stack.callback(v_2.destroy)
            with pytest.raises(RuntimeError, match='Ambiguous'):
                _ = Volume.from_any_id('1234567', strict=False)

    def test09_clone_already_exists(self):
        with ExitStack() as stack:
            base = Image.from_tag('freebsd-latest')
            im = Image.clone_from(base, sha256='1234567xxx')
            stack.callback(im.destroy)
            with pytest.raises(RuntimeError, match='already exists'):
                im = Image.clone_from(base, sha256='1234567xxx')

    def test10_ambiguous_noraise(self):
        with ExitStack() as stack:
            base = Image.from_tag('freebsd-latest')
            im = Image.clone_from(base)
            stack.callback(im.destroy)
            im.add_tags(['freebsd-latest-focker-unit-test-dataset'])
            res = Image.from_any_id('freebsd-latest', strict=False, raise_exc=False)
            assert res is None

    def test11_exists_ambiguous_raise(self):
        with ExitStack() as stack:
            base = Image.from_tag('freebsd-latest')
            im = Image.clone_from(base)
            stack.callback(im.destroy)
            im.add_tags(['freebsd-latest-focker-unit-test-dataset'])
            with pytest.raises(RuntimeError, match='Ambiguous'):
                _ = Image.exists_predicate(lambda im: any(t.startswith('freebsd-latest') for t in im[3].split(' ')))

    def test12_from_partial_sha256(self):
        with ExitStack() as stack:
            base = Image.from_tag('freebsd-latest')
            im = Image.clone_from(base, sha256='1234567xxx')
            stack.callback(im.destroy)
            im_2 = Image.from_partial_sha256('1234567')
            assert im_2.path == im.path

    def test13_from_partial_tag(self):
        with ExitStack() as stack:
            base = Image.from_tag('freebsd-latest')
            im = Image.clone_from(base, sha256='1234567xxx')
            stack.callback(im.destroy)
            im.add_tags([ 'focker-unit-test-dataset-123' ])
            im_2 = Image.from_partial_tag('focker-unit-test-dataset')
            assert im_2.path == im.path

    def test14_remove_tags_none(self):
        with ExitStack() as stack:
            base = Image.from_tag('freebsd-latest')
            im = Image.clone_from(base, sha256='1234567xxx')
            stack.callback(im.destroy)
            im.add_tags([ 'focker-unit-test-dataset-123' ])
            im.remove_tags(None)
            assert im.tags == { 'focker-unit-test-dataset-123' }

    def test15_remove_tags_missing(self):
        with ExitStack() as stack:
            base = Image.from_tag('freebsd-latest')
            im = Image.clone_from(base, sha256='1234567xxx')
            stack.callback(im.destroy)
            im.add_tags([ 'focker-unit-test-dataset-123' ])
            with pytest.raises(RuntimeError, match='all the specified tags'):
                im.remove_tags([ 'focker-unit-test-dataset-123', 'focker-unit-test-dataset-456' ])

    def test16_in_use_cannot_destroy(self):
        with ExitStack() as stack:
            base = Image.from_tag('freebsd-latest')
            im_1 = Image.clone_from(base)
            stack.callback(im_1.destroy)
            im_1.finalize()
            im_2 = Image.clone_from(im_1)
            stack.callback(im_2.destroy)
            with pytest.raises(RuntimeError, match='is in use'):
                im_1.destroy()

    def test17_in_use_non_existing(self):
        v = Volume.create()
        zfs_destroy(v.name)
        assert not zfs_exists(v.name)
        assert not v.in_use()

    def test18_test_new_props(self):
        with ExitStack() as stack:
            base_im = Image.from_tag('freebsd-latest')
            im = Image.clone_from(base_im)
            stack.callback(im.destroy)
            assert im.origin.sha256 == base_im.sha256
            assert im.origin_sha256 == base_im.sha256
            assert im.origin_mountpoint == base_im.mountpoint
            assert im.origin_tags == base_im.tags
            assert im.referred_size == base_im.referred_size
