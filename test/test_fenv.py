from focker.core.image.steps import RunStep, \
    CopyStep, \
    CopyStepEntry
from focker.core.image import ImageBuilder, \
    Image
from focker.core import Volume, \
    JailFs, \
    OSJail
from focker.core.fenv import substitute_focker_env_vars, \
    fenv_from_file, \
    fenv_from_list, \
    fenv_from_arg, \
    lower_keys, \
    rec_subst_fenv_vars
import tempfile
import os
import focker.yaml as yaml
from contextlib import ExitStack
import pytest
from focker.__main__ import main
import stat


class TestFEnv:
    def test01_run_step_list(self):
        spec = [
            'ls -al ${{ FOO }}',
            'mv -iv ${{ FOO }} ${{ BAZ }}'
        ]
        src_dir = '.'
        fenv = {
            'foo': 'bar',
            'baz': 'lorem'
        }
        step = RunStep(spec, src_dir, fenv)
        assert step.spec == [ 'ls -al bar', 'mv -iv bar lorem' ]

    def test02_run_step_single(self):
        spec = 'ls -al ${{ FOO }} && mv -iv ${{ FOO }} ${{ BAZ }}'
        src_dir = '.'
        fenv = {
            'foo': 'bar',
            'baz': 'lorem'
        }
        step = RunStep(spec, src_dir, fenv)
        assert step.spec == 'ls -al bar && mv -iv bar lorem'

    def test03_run_step_in_fockerfile(self):
        with tempfile.TemporaryDirectory() as d, \
            ExitStack() as stack:

            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump({
                    'base': 'freebsd-latest',
                    'fenv': {
                        'foo': 'bar',
                        'baz': 'lorem'
                    },
                    'steps': [
                        { 'run': 'echo "${{ FOO }}" >/.foo && echo "${{ FOO }} ${{ BAZ }}" >/.baz' }
                    ]
                }, f)

            bld = ImageBuilder(d, fenv={ 'baz': 'ipsum' })
            im = bld.build()
            stack.callback(im.destroy)

            assert os.path.exists(os.path.join(im.path, '.foo'))
            assert os.path.exists(os.path.join(im.path, '.baz'))
            with open(os.path.join(im.path, '.foo')) as f:
                assert f.read().strip() == 'bar'
            with open(os.path.join(im.path, '.baz')) as f:
                assert f.read().strip() == 'bar ipsum'

    def test04_copy_step_list(self):
        with tempfile.TemporaryDirectory() as d, \
            ExitStack() as stack:

            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump({
                    'base': 'freebsd-latest',
                    'fenv': {
                        'foo': 'bar',
                        'baz': 'lorem'
                    },
                    'steps': [
                        { 'copy': [
                            [ './foo', '/.foo'],
                            [ './baz', '/.baz', { 'use_fenv': True } ]
                        ] }
                    ]
                }, f)

            with open(os.path.join(d, 'foo'), 'w') as f:
                f.write('${{ FOO }} has ${{ BAZ }}')

            with open(os.path.join(d, 'baz'), 'w') as f:
                f.write('${{ BAZ }} has ${{ FOO }}')

            bld = ImageBuilder(d, fenv={ 'baz': 'ipsum' })
            im = bld.build()
            stack.callback(im.destroy)

            assert os.path.exists(os.path.join(im.path, '.foo'))
            assert os.path.exists(os.path.join(im.path, '.baz'))
            with open(os.path.join(im.path, '.foo')) as f:
                assert f.read().strip() == '${{ FOO }} has ${{ BAZ }}'
            with open(os.path.join(im.path, '.baz')) as f:
                assert f.read().strip() == 'ipsum has bar'

    def test05_fenv_corner_cases(self):
        fenv = {
            'foo': 'lorem',
            'bar': 'ipsum'
        }
        assert substitute_focker_env_vars('x${{}}y', fenv) == 'xy'
        assert substitute_focker_env_vars('x${{     }}y', fenv) == 'xy'
        assert substitute_focker_env_vars('x${{  \n\n\n   }}y', fenv) == 'xy'
        assert substitute_focker_env_vars('x${{  \n\n\n;   }}y', fenv) == 'x${{  \n\n\n;   }}y'
        assert substitute_focker_env_vars('x ${{  FOO  }} y', fenv) == 'x lorem y'
        assert substitute_focker_env_vars('x ${{  FOO  }} ${{ BAR }} y', fenv) == 'x lorem ipsum y'
        assert substitute_focker_env_vars('x ${{  ${{ }} y', fenv) == 'x ${{   y'
        assert substitute_focker_env_vars('x ${{ }} }} y', fenv) == 'x  }} y'
        assert substitute_focker_env_vars('x ${{ ${{ }} }} y', fenv) == 'x ${{  }} y'
        assert substitute_focker_env_vars('x ${{ ala ma kota }} y', fenv) == 'x ${{ ala ma kota }} y'
        with pytest.raises(KeyError):
            _ = substitute_focker_env_vars('x ${{ alamakota }} y', fenv)
        assert substitute_focker_env_vars('x ${{ "alamakota" }} y', fenv) == 'x alamakota y'
        assert substitute_focker_env_vars("x ${{ 'alamakota' }} y", fenv) == 'x alamakota y'
        assert substitute_focker_env_vars("x ${{ 'alamakota\" }} y", fenv) == 'x ${{ \'alamakota" }} y'
        assert substitute_focker_env_vars("x ${{ '${{ alamakota }}' }} y", fenv) == 'x ${{ alamakota }} y'

    def test06_fenv_from_file(self):
        with tempfile.NamedTemporaryFile() as f:
            yaml.safe_dump({'FoO': 'lorem', 'bAr': 'ipsum', 'baF': 'sit' }, f)
            f.flush()
            fenv = fenv_from_file(f.name, lower_keys({ 'baz': 'dolor', 'Baf': 'amet' }))
            assert fenv == { 'foo': 'lorem', 'bar': 'ipsum', 'baz': 'dolor', 'baf': 'amet' }

    def test07_copy_step_entry(self):
        with pytest.raises(TypeError, match='list'):
            _ = CopyStepEntry('bad-spec', '.', {})
        too_short_spec = []
        with pytest.raises(ValueError, match='elements'):
            _ = CopyStepEntry(too_short_spec, '.', {})
        too_long_spec = [ 1, 2, 3, 4 ]
        with pytest.raises(ValueError, match='elements'):
            _ = CopyStepEntry(too_long_spec, '.', {})

    def _compose_build_hook_test(self, hook_name):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, 'focker-compose.yml'), 'w') as f:
                yaml.safe_dump({
                    hook_name: 'echo ${{ foobar }} ${{ lorem }} >"%s/.focker-unit-test-fenv"' % d,
                    'fenv': {
                        'foobar': 'bazbaf'
                    }
                }, f)
            main([ 'compose', 'build', os.path.join(d, 'focker-compose.yml'), '--fenv', 'lorem', 'ipsum' ])
            assert os.path.exists(os.path.join(d, '.focker-unit-test-fenv'))
            with open(os.path.join(d, '.focker-unit-test-fenv')) as f:
                assert f.read().strip() == 'bazbaf ipsum'

    def test08_compose_build_exec_prebuild(self):
        return self._compose_build_hook_test('exec.prebuild')

    def test09_compose_build_exec_postbuild(self):
        return self._compose_build_hook_test('exec.postbuild')

    def test10_compose_build_image(self):
        with tempfile.TemporaryDirectory() as d, \
            ExitStack() as stack:

            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump({
                    'base': 'freebsd-latest',
                    'fenv': {
                        'foobar': 'amet',
                        'lorem': 'adpiscin',
                        'dolor': 'sit'
                    },
                    'steps': [
                        { 'run': 'echo ${{ foobar }} ${{ lorem }} ${{ dolor }} >/.focker-unit-test-fenv' }
                    ]
                }, f)

            with open(os.path.join(d, 'focker-compose.yml'), 'w') as f:
                yaml.safe_dump({
                    'images': {
                        'focker-unit-test-fenv': '.'
                    },
                    'fenv': {
                        'foobar': 'bazbaf'
                    }
                }, f)

            main([ 'compose', 'build', os.path.join(d, 'focker-compose.yml'), '--fenv', 'lorem', 'ipsum' ])
            im = Image.from_tag('focker-unit-test-fenv')
            stack.callback(im.destroy)

            assert os.path.exists(os.path.join(im.path, '.focker-unit-test-fenv'))
            with open(os.path.join(im.path, '.focker-unit-test-fenv')) as f:
                assert f.read().strip() == 'bazbaf ipsum sit'

    def test11_compose_build_volume(self):
        with tempfile.TemporaryDirectory() as d, \
            ExitStack() as stack:

            with open(os.path.join(d, 'focker-compose.yml'), 'w') as f:
                yaml.safe_dump({
                    'volumes': {
                        'focker-unit-test-fenv': {
                            'chown': '${{ UID }}:${{ GID }}',
                            'chmod': '${{ PERMS }}'
                        }
                    },
                    'fenv': {
                        'uid': '80',
                        'perms': '0742',
                    }
                }, f)

            main([ 'compose', 'build', os.path.join(d, 'focker-compose.yml'),
                '--fenv', 'gid', '1000', 'uid', '1000' ])
            v = Volume.from_tag('focker-unit-test-fenv')
            stack.callback(v.destroy)

            assert os.path.exists(v.path)
            st = os.stat(v.path)
            assert stat.S_ISDIR(st.st_mode)
            assert stat.S_IMODE(st.st_mode) == 0o742
            assert st.st_uid == 1000
            assert st.st_gid == 1000

    def test12_compose_build_jail(self):
        with tempfile.TemporaryDirectory() as d, \
            ExitStack() as stack:

            with open(os.path.join(d, 'focker-compose.yml'), 'w') as f:
                yaml.safe_dump({
                    'jails': {
                        'focker-unit-test-fenv': {
                            'image': '${{ IMAGE }}',
                            'exec.start': 'echo ${{ EXEC_START_TEXT }} >/.focker-unit-test-fenv',
                            'exec.fib': '${{ EXEC_FIB }}'
                        }
                    },
                    'fenv': {
                        'IMAGE': 'foobar',
                        'EXEC_START_TEXT': 'foobar',
                        'EXEC_FIB': '1'
                    }
                }, f)

            main([ 'compose', 'build', os.path.join(d, 'focker-compose.yml'),
                '--fenv', 'iMaGe', 'freebsd-latest', 'exec_fib', '0' ])
            jfs = JailFs.from_tag('focker-unit-test-fenv')
            stack.callback(jfs.destroy)
            j = OSJail.from_tag('focker-unit-test-fenv')
            jc = j.conf
            im = Image.from_tag('freebsd-latest')
            assert jfs.get_props([ 'origin' ])['origin'].split('@')[0] == im.name
            # assert jc['path'] == im.path
            assert jc['exec.start'] == 'echo foobar >/.focker-unit-test-fenv'
            assert isinstance(jc['exec.fib'], int)
            assert jc['exec.fib'] == 0

    def test13_fenv_rec_subst_corner_cases(self):
        lst = rec_subst_fenv_vars([ '${{ FOO }}', '${{ BAR }}', '${{ BAF }}' ],
            { 'foo': 'lorem', 'bar': 'ipsum', 'baf': 'dolor' })
        assert isinstance(lst, list)
        assert lst == [ 'lorem', 'ipsum', 'dolor' ]

        s = rec_subst_fenv_vars({ '${{ FOO }}', '${{ BAR }}', '${{ BAF }}' },
            { 'foo': 'lorem', 'bar': 'ipsum', 'baf': 'dolor' })
        assert isinstance(s, set)
        assert s == { 'lorem', 'ipsum', 'dolor' }

    def test14_fenv_from_list_raise(self):
        with pytest.raises(ValueError, match='divisible by 2'):
            _ = fenv_from_list([ 'a', 'b', 'c' ], {})

    def test15_fenv_from_arg_raise(self):
        with pytest.raises(TypeError, match='list'):
            _ = fenv_from_arg('alamakota', {})

    def test16_fenv_from_arg_file_fallback(self):
        with tempfile.NamedTemporaryFile() as f:
            yaml.safe_dump({ 'foo': 'lorem' }, f)
            fenv = fenv_from_arg([ f.name ], {})
            assert len(fenv) == 1
            assert 'foo' in fenv
            assert fenv['foo'] == 'lorem'
