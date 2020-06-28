from focker.steps import RunStep, \
    CopyStep
import subprocess
import pytest
from focker.zfs import zfs_find
import os


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
