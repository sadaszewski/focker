from focker.compose import exec_hook, \
    exec_prebuild, \
    exec_postbuild, \
    build_volumes, \
    build_images
from tempfile import TemporaryDirectory
import os
import pytest
import fcntl
from focker.misc import focker_lock, \
    focker_unlock
import inspect
import ast
import stat
from focker.zfs import zfs_find, \
    zfs_mountpoint, \
    zfs_parse_output
import subprocess
import yaml


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


def test_build_volumes():
    subprocess.check_output(['focker', 'volume', 'remove', '--force', 'test-build-volumes'])
    err = False
    try:
        name, _ = zfs_find('test-build-volumes', focker_type='volume')
    except:
        err = True
    assert err
    spec = {
        'test-build-volumes': {
            'chown': '65534:65534',
            'chmod': 0o123,
            'zfs': {
                'quota': '1G',
                'readonly': 'on'
            }
        }
    }
    build_volumes(spec)
    name, _ = zfs_find('test-build-volumes', focker_type='volume')
    st = os.stat(zfs_mountpoint(name))
    assert st.st_uid == 65534
    assert st.st_gid == 65534
    assert ('%o' % st.st_mode)[-3:] == '123'
    zst = zfs_parse_output(['zfs', 'get', '-H', 'quota,readonly', name])
    assert zst[0][2] == '1G'
    assert zst[1][2] == 'on'
    subprocess.check_output(['zfs', 'destroy', '-r', '-f', name])


def test_build_images():
    subprocess.check_output(['focker', 'image', 'remove', '--force', 'test-focker-bootstrap'])
    subprocess.check_output(['focker', 'bootstrap', '--dry-run', '--tags', 'test-focker-bootstrap'])
    subprocess.check_output(['focker', 'image', 'remove', '--force', 'test-build-images'])
    with TemporaryDirectory() as d:
        with open(os.path.join(d, 'Fockerfile'), 'w') as f:
            yaml.dump({
                'base': 'test-focker-bootstrap',
                'steps': [
                    { 'copy': [
                        [ '/bin/sh', '/bin/sh', { 'chmod': 0o777 } ],
                        [ '/lib/libedit.so.7', '/lib/libedit.so.7' ],
                        [ '/lib/libncursesw.so.8', '/lib/libncursesw.so.8' ],
                        [ '/lib/libc.so.7', '/lib/libc.so.7' ],
                        [ '/usr/bin/touch', '/usr/bin/touch', { 'chmod': 0o777 } ],
                        [ '/libexec/ld-elf.so.1', '/libexec/ld-elf.so.1', { 'chmod': 0o555 } ]
                    ] },
                    { 'run': 'touch /test-build-images' }
                ]
            }, f)
        args = lambda: 0
        args.squeeze = False
        build_images({
            'test-build-images': '.'
        }, d, args)
    focker_unlock()
    name, _ = zfs_find('test-build-images', focker_type='image')
    assert os.path.exists(os.path.join(zfs_mountpoint(name), 'test-build-images'))
    subprocess.check_output(['focker', 'image', 'remove', '--force', 'test-build-images'])
    subprocess.check_output(['focker', 'image', 'prune'])
    subprocess.check_output(['focker', 'image', 'remove', '--force', 'test-focker-bootstrap'])
