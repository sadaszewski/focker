from dataset_test_base import DatasetTestBase
from dataset_cmd_test_base import DatasetCmdTestBase
from focker.core import Image, \
    CalledProcessError
from focker.core.image.steps import RunStep, \
    CopyStep, \
    create_step
import focker.yaml as yaml
from focker.__main__ import main
from tempfile import TemporaryDirectory
import os
import stat
import pytest
from contextlib import ExitStack


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

    def test25_facets(self):
        with TemporaryDirectory() as d, \
            ExitStack() as stack:
            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump({
                    'base': 'freebsd-latest',
                    'facets': [ './facet_01.yml', './facet_02.yml' ]
                }, f)
            with open(os.path.join(d, 'facet_01.yml'), 'w') as f:
                yaml.safe_dump({
                    'steps': {
                        12: [ { 'run': 'touch /.focker-unit-test-image-facet-01' } ]
                    }
                }, f)
            with open(os.path.join(d, 'facet_02.yml'), 'w') as f:
                yaml.safe_dump({
                    'steps': {
                        10: [ { 'run': 'touch /.focker-unit-test-image-facet-02' } ]
                    }
                }, f)

            cmd = [ 'image', 'build', d, '-t', 'focker-unit-test-image-facets' ]
            main(cmd)
            im = Image.from_tag('focker-unit-test-image-facets')
            stack.callback(im.destroy)
            st_1 = os.stat(os.path.join(im.path, '.focker-unit-test-image-facet-01'))
            st_2 = os.stat(os.path.join(im.path, '.focker-unit-test-image-facet-02'))
            assert st_2.st_mtime < st_1.st_mtime

    def test26_facets_missing_steps(self):
        with TemporaryDirectory() as d:
            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump({
                    'base': 'freebsd-latest',
                    'facets': [ './facet_01.yml', './facet_02.yml' ]
                }, f)
            with open(os.path.join(d, 'facet_01.yml'), 'w') as f:
                yaml.safe_dump({}, f)
            with open(os.path.join(d, 'facet_02.yml'), 'w') as f:
                yaml.safe_dump({
                    'steps': {
                        10: [ { 'run': 'touch /.focker-unit-test-image-facet-02' } ]
                    }
                }, f)

            cmd = [ 'image', 'build', d, '-t', 'focker-unit-test-image-facets' ]
            with pytest.raises(KeyError, match='steps'):
                main(cmd)

    def test27_facets_not_same_convention(self):
        with TemporaryDirectory() as d:
            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump({
                    'base': 'freebsd-latest',
                    'facets': [ './facet_01.yml', './facet_02.yml' ]
                }, f)
            with open(os.path.join(d, 'facet_01.yml'), 'w') as f:
                yaml.safe_dump({
                    'steps': [
                        { 'run': 'touch /.focker-unit-test-image-facet-01' }
                    ]
                }, f)
            with open(os.path.join(d, 'facet_02.yml'), 'w') as f:
                yaml.safe_dump({
                    'steps': {
                        10: [ { 'run': 'touch /.focker-unit-test-image-facet-02' } ]
                    }
                }, f)

            cmd = [ 'image', 'build', d, '-t', 'focker-unit-test-image-facets' ]
            with pytest.raises(TypeError, match='same convention'):
                main(cmd)

    def test28_facets_list(self):
        with TemporaryDirectory() as d, \
            ExitStack() as stack:
            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump({
                    'base': 'freebsd-latest',
                    'facets': [ './facet_01.yml', './facet_02.yml' ]
                }, f)
            with open(os.path.join(d, 'facet_01.yml'), 'w') as f:
                yaml.safe_dump({
                    'steps': [
                        { 'run': 'touch /.focker-unit-test-image-facet-01' }
                    ]
                }, f)
            with open(os.path.join(d, 'facet_02.yml'), 'w') as f:
                yaml.safe_dump({
                    'steps': [
                        { 'run': 'touch /.focker-unit-test-image-facet-02' }
                    ]
                }, f)

            cmd = [ 'image', 'build', d, '-t', 'focker-unit-test-image-facets' ]
            main(cmd)
            im = Image.from_tag('focker-unit-test-image-facets')
            stack.callback(im.destroy)
            st_1 = os.stat(os.path.join(im.path, '.focker-unit-test-image-facet-01'))
            st_2 = os.stat(os.path.join(im.path, '.focker-unit-test-image-facet-02'))
            assert st_2.st_mtime > st_1.st_mtime

    def test29_facets_wrong_convention(self):
        with TemporaryDirectory() as d:
            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump({
                    'base': 'freebsd-latest',
                    'facets': [ './facet_01.yml' ]
                }, f)
            with open(os.path.join(d, 'facet_01.yml'), 'w') as f:
                yaml.safe_dump({
                    'steps': { 'touch /.focker-unit-test-image-facet-01' }
                }, f)

            cmd = [ 'image', 'build', d, '-t', 'focker-unit-test-image-facets' ]
            with pytest.raises(TypeError, match='Unsupported'):
                main(cmd)


class TestBuildSteps:
    def test01_run_step_spec_type(self):
        with pytest.raises(TypeError):
            _ = RunStep(1, '.')
        _ = RunStep('ls -al', '.')

    def test02_copy_step_spec_type(self):
        with pytest.raises(TypeError):
            _ = CopyStep(1, '.')
        _ = CopyStep([], '.')

    def test03_copy_step_empty_hash(self):
        assert CopyStep([], '.').hash('1234567xxx') == '70ddf44f1f2ec9d11d7650fc1569707c08e577562fc7fdeb8f03c5cf6ee3a69b'

    def test04_single_copy_hash(self):
        with TemporaryDirectory() as d:
            with open(os.path.join(d, 'a.file'), 'w') as f:
                pass
            assert CopyStep([ 'a.file', '/a.file' ], d).hash('1234567xxx') == \
                'f0cc46f43a0943125635fee1d056de9a8eec0bb4980d071990342501a58e199c'

    def test05_create_step_type_error(self):
        with pytest.raises(TypeError, match='must be a dictionary'):
            _ = create_step(1, '.')

    def test06_unrecognized_step(self):
        with pytest.raises(ValueError, match='Unrecognized'):
            _ = create_step({ 'xxx': {} }, '')
