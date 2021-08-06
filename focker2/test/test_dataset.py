from focker.core import Image, \
    Volume
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
