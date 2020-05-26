from focker.compose import exec_hook, \
    exec_prebuild, \
    exec_postbuild
from tempfile import TemporaryDirectory
import os
import pytest
import fcntl
from focker.misc import focker_lock, \
    focker_unlock
import inspect
import ast


def test_exec_hook_01():
    spec = [
        'touch test-exec-hook-01',
        'touch test-exec-hook-02'
    ]
    with TemporaryDirectory() as d:
        exec_hook(spec, d, 'test-exec-hook')
        assert os.path.exists(os.path.join(d, 'test-exec-hook-01'))
        assert os.path.exists(os.path.join(d, 'test-exec-hook-02'))
    assert not os.path.exists(d)


def test_exec_hook_02():
    spec = 'touch test-exec-hook-01 && touch test-exec-hook-02'
    with TemporaryDirectory() as d:
        exec_hook(spec, d, 'test-exec-hook')
        assert os.path.exists(os.path.join(d, 'test-exec-hook-01'))
        assert os.path.exists(os.path.join(d, 'test-exec-hook-02'))
    assert not os.path.exists(d)


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_exec_hook_03a():
    spec = 1
    with TemporaryDirectory() as d:
        exec_hook(spec, d, 'test-exec-hook')


@pytest.mark.xfail(raises=TypeError, strict=True)
def test_exec_hook_03b():
    spec = [1]
    with TemporaryDirectory() as d:
        exec_hook(spec, d, 'test-exec-hook')


@pytest.mark.xfail(raises=FileNotFoundError, strict=True)
def test_exec_hook_04():
    spec = 'ls'
    exec_hook(spec, '/non-existent-directory/wcj20fy103', 'test-exec-hook')


def test_exec_hook_05():
    spec = 'ls'
    oldwd = os.getcwd()
    with TemporaryDirectory() as d:
        exec_hook(spec, d, 'test-exec-hook')
    assert os.getcwd() == oldwd


@pytest.mark.xfail(raises=RuntimeError, strict=True)
def test_exec_hook_06():
    spec = '/non-existent-command/hf249h'
    with TemporaryDirectory() as d:
        exec_hook(spec, d, 'test-exec-hook')


def test_exec_hook_07():
    os.chdir('/')
    spec = 'flock --nonblock /var/lock/focker.lock -c ls'
    focker_lock()
    assert fcntl.flock(focker_lock.fd, fcntl.LOCK_EX | fcntl.LOCK_NB) != 0
    with TemporaryDirectory() as d:
        exec_hook(spec, d, 'test-exec-hook')
    assert fcntl.flock(focker_lock.fd, fcntl.LOCK_EX | fcntl.LOCK_NB) != 0
    focker_unlock()


def _test_simple_forward(fun, fwd_fun_name='exec_hook'):
    src = inspect.getsource(fun)
    mod = ast.parse(src)
    assert isinstance(mod.body[0], ast.FunctionDef)
    assert isinstance(mod.body[0].body[0], ast.Return)
    assert isinstance(mod.body[0].body[0].value, ast.Call)
    assert mod.body[0].body[0].value.func.id == fwd_fun_name


def test_exec_prebuild():
    _test_simple_forward(exec_prebuild)


def test_exec_postbuild():
    _test_simple_forward(exec_postbuild)
