from focker.core.image.steps import RunStep, \
    CopyStep
from focker.core.image import ImageBuilder
import tempfile
import os
import focker.yaml as yaml
from contextlib import ExitStack


class TestFEnv:
    def test01_run_step_list(self):
        spec = [
            'ls -al {{ FOO }}',
            'mv -iv {{ FOO }} {{ BAZ }}'
        ]
        src_dir = '.'
        fenv = {
            'foo': 'bar',
            'baz': 'lorem'
        }
        step = RunStep(spec, src_dir, fenv)
        assert step.spec == [ 'ls -al bar', 'mv -iv bar lorem' ]

    def test02_run_step_single(self):
        spec = 'ls -al {{ FOO }} && mv -iv {{ FOO }} {{ BAZ }}'
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
                        { 'run': 'echo "{{ FOO }}" >/.foo && echo "{{ FOO }} {{ BAZ }}" >/.baz' }
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
