from focker.steps import RunStep, \
    CopyStep, \
    create_step
import subprocess
import pytest
from focker.zfs import zfs_find
import os
import tempfile
from focker.misc import random_sha256_hexdigest


def setup_module(module):
    subprocess.check_output(['focker', 'bootstrap', '--non-interactive', '--tags', 'test-steps'])


def teardown_module(module):
    subprocess.check_output(['focker', 'image', 'remove', 'test-steps'])


def test_run_step_01():
    base_name, base_sha256 = zfs_find('test-steps', focker_type='image')
    spec = [
        'echo test-run-step-01 >/test.txt'
    ]
    step = RunStep(spec)
    step_sha256 = step.hash(base_sha256)
    step_name = 'zroot/focker/images/test-run-step-01'
    subprocess.check_output(['zfs', 'clone', '-o', f'focker:sha256={step_sha256}', f'{base_name}@1', step_name])
    step_path = '/focker/images/test-run-step-01'
    step.execute(step_path)
    assert os.path.exists(os.path.join(step_path, 'test.txt'))
    with open(os.path.join(step_path, 'test.txt'), 'r') as f:
        assert f.read() == 'test-run-step-01\n'
    subprocess.check_output(['zfs', 'destroy', step_name])


def test_run_step_02():
    with pytest.raises(ValueError) as excinfo:
        _ = RunStep(None)
    assert excinfo.value.args == ('Run spec must be a list or a string',)


def test_copy_step_01():
    with pytest.raises(ValueError) as excinfo:
        _ = CopyStep(None)
    assert excinfo.value.args == ('CopyStep spec should be a list',)


def test_copy_step_02():
    base_sha256 = random_sha256_hexdigest()
    with tempfile.TemporaryDirectory() as d1:
        with tempfile.TemporaryDirectory() as d2:
            args = lambda: 0
            args.focker_dir = d1
            with open(os.path.join(d1, 'test.txt'), 'w') as f:
                f.write('test-copy-step-02')
            step = CopyStep([
                [ os.path.join(d1, 'test.txt'), '/test.txt',
                    {'chmod': 0o777, 'chown': '65534:65534'} ]
            ])
            _ = step.hash(base_sha256, args)
            step.execute(d2, args=args)
            with open(os.path.join(d2, 'test.txt'), 'r') as f:
                assert f.read() == 'test-copy-step-02'
            st = os.stat(os.path.join(d2, 'test.txt'))
            assert (st.st_mode & 0o777) == 0o777
            assert st.st_uid == 65534
            assert st.st_gid == 65534


def test_copy_step_03():
    step = CopyStep([
        '/etc/hosts', '/foo/bar'
    ])
    args = lambda: 0
    args.focker_dir = '/bar/baz'
    _ = step.hash(random_sha256_hexdigest(), args)


def test_copy_step_04():
    step = CopyStep([])
    args = lambda: 0
    args.focker_dir = '/bar/baz'
    _ = step.hash(random_sha256_hexdigest(), args)


def test_create_step_01():
    with pytest.raises(ValueError) as excinfo:
        create_step(None)
    assert excinfo.value.args == ('Step specification must be a dictionary',)


def test_create_step_02():
    spec = {
        'copy': ['/no/path', '/foo/bar']
    }
    step = create_step(spec)
    assert isinstance(step, CopyStep)


def test_create_step_03():
    spec = {
        'run': [ 'echo test-create-step-03' ]
    }
    step = create_step(spec)
    assert isinstance(step, RunStep)
