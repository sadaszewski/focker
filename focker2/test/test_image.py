from dataset_test_base import DatasetTestBase
from dataset_cmd_test_base import DatasetCmdTestBase
from focker.core import Image, \
    CalledProcessError
import focker.yaml as yaml
from focker.__main__ import main
from tempfile import TemporaryDirectory
import os
import stat
import pytest


class TestImage(DatasetTestBase):
    _meta_class = Image


class TestImageCmd(DatasetCmdTestBase):
    _meta_class = Image

    def test16_build(self):
        with TemporaryDirectory() as d:
            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump(dict(
                    base='freebsd-latest',
                    steps=[
                        dict(run=[
                            'touch /.focker-unit-test'
                        ])
                    ]
                ), f)
            cmd = [ 'image', 'build', d, '-t', 'focker-unit-test-image' ]
            main(cmd)
            assert Image.exists_tag('focker-unit-test-image')
            im = Image.from_tag('focker-unit-test-image')
            try:
                assert os.path.exists(os.path.join(im.path, '.focker-unit-test'))
            finally:
                im.destroy()

    def test17_build_with_copy(self):
        with TemporaryDirectory() as d:
            with open(os.path.join(d, 'dummyfile'), 'w') as f:
                f.write('focker-unit-test-image-build\n')
            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump(dict(
                    base='freebsd-latest',
                    steps=[
                        dict(copy=[
                            [ 'dummyfile', '/etc/dummyfile', { 'chown': '65534:65534', 'chmod': 0o600 } ]
                        ])
                    ]
                ), f)
            cmd = [ 'image', 'build', d, '-t', 'focker-unit-test-image' ]
            main(cmd)
            assert Image.exists_tag('focker-unit-test-image')
            im = Image.from_tag('focker-unit-test-image')
            try:
                fnam = os.path.join(im.path, 'etc/dummyfile')
                assert os.path.exists(fnam)
                with open(fnam) as f:
                    assert f.read() == 'focker-unit-test-image-build\n'
                st = os.stat(fnam)
                assert stat.S_IMODE(st.st_mode) == 0o600
                assert st.st_uid == 65534
                assert st.st_gid == 65534
            finally:
                im.destroy()

    def test18_build_validate(self):
        with TemporaryDirectory() as d:
            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump({}, f)

            cmd = [ 'image', 'build', d ]
            with pytest.raises(RuntimeError, match='Missing base'):
                main(cmd)

            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump({ 'base': 'freebsd-latest' }, f)

            cmd = [ 'image', 'build', d ]
            with pytest.raises(RuntimeError, match='Exactly one'):
                main(cmd)

    def test19_build_no_fockerfile(self):
        with TemporaryDirectory() as d:
            cmd = [ 'image', 'build', d ]
            with pytest.raises(RuntimeError, match='Fockerfile not found'):
                main(cmd)

    def test20_build_dict_steps(self):
        with TemporaryDirectory() as d:
            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump({
                    'base': 'freebsd-latest',
                    'steps': {
                        3: [ { 'run': 'echo 3 >>/.focker-unit-test-image-build-dict-steps' } ],
                        2: [ { 'run': 'echo 2 >>/.focker-unit-test-image-build-dict-steps' } ],
                        1: [ { 'run': 'echo 1 >>/.focker-unit-test-image-build-dict-steps' } ]
                    }
                }, f)

            cmd = [ 'image', 'build', d, '-t', 'focker-unit-test-image-build-dict-steps' ]
            main(cmd)
            im = Image.from_tag('focker-unit-test-image-build-dict-steps')
            try:
                assert os.path.exists(os.path.join(im.path, '.focker-unit-test-image-build-dict-steps'))
                with open (os.path.join(im.path, '.focker-unit-test-image-build-dict-steps')) as f:
                    data = f.read()
                assert data.replace('\r', '') == '1\n2\n3\n'
            finally:
                im.destroy()

    def test21_build_list_expected(self):
        with TemporaryDirectory() as d:
            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump({
                    'base': 'freebsd-latest',
                    'steps': { 'run': 'echo foo >>/.focker-unit-test-image-build' }
                }, f)

            cmd = [ 'image', 'build', d ]
            with pytest.raises(TypeError, match='Expected list/s'):
                main(cmd)

    def test22_build_squeeze(self):
        with TemporaryDirectory() as d:
            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump({
                    'base': 'freebsd-latest',
                    'steps': [
                        { 'run': 'echo foo >>/.focker-unit-test-image-build' },
                        { 'run': 'echo bar >>/.focker-unit-test-image-build' }
                    ]
                }, f)

            cmd = [ 'image', 'build', d, '-t', 'focker-unit-test-image-build-squeeze', '--squeeze' ]
            main(cmd)
            im = Image.from_tag('focker-unit-test-image-build-squeeze')
            try:
                origin = im.get_props([ 'origin' ])['origin']
                base = Image.from_tag('freebsd-latest')
                assert origin == base.snapshot_name
                with open(os.path.join(im.path, '.focker-unit-test-image-build')) as f:
                    data = f.read()
                assert data.replace('\r', '') == 'foo\nbar\n'
            finally:
                im.destroy()

    def test23_build_exists(self):
        with TemporaryDirectory() as d:
            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump({
                    'base': 'freebsd-latest',
                    'steps': [ { 'run': 'echo foo >>/.focker-unit-test-image-build' } ]
                }, f)

            cmd = [ 'image', 'build', d, '-t', 'focker-unit-test-image-build' ]
            main(cmd)
            im = Image.from_tag('focker-unit-test-image-build')
            try:
                st = os.stat(os.path.join(im.path, '.focker-unit-test-image-build'))
                old_mtime = st.st_mtime
                main(cmd)
                st = os.stat(os.path.join(im.path, '.focker-unit-test-image-build'))
                assert st.st_mtime == old_mtime
                im.set_props({ 'rdonly': 'off' })
                os.system(f'touch {os.path.join(im.path, ".focker-unit-test-image-build")}')
                st = os.stat(os.path.join(im.path, '.focker-unit-test-image-build'))
                assert st.st_mtime != old_mtime
            finally:
                im.destroy()

    def test24_build_fail(self):
        with TemporaryDirectory() as d:
            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump({
                    'base': 'freebsd-latest',
                    'steps': [ { 'run': 'no-such-command' } ]
                }, f)

            cmd = [ 'image', 'build', d ]
            with pytest.raises(CalledProcessError):
                main(cmd)
