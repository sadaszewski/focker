import subprocess
from focker.zfs import *
import re
import os
from focker.bootstrap import command_bootstrap, \
    bootstrap_empty, \
    _bootstrap_common
from focker.misc import focker_unlock
import pytest
import focker.bootstrap
import hashlib


def test_bootstrap_01():
    subprocess.check_output(['focker', 'image', 'remove', '--force', 'test-focker-bootstrap'])
    subprocess.check_output(['focker', 'bootstrap', '--empty', '--tags', 'test-focker-bootstrap'])
    name, sha256 = zfs_find('test-focker-bootstrap', focker_type='image')
    basename = os.path.basename(name)
    assert 7 <= len(basename) <= 64
    assert re.search('[a-f]', basename[:7])
    assert len(sha256) == 64
    assert basename == sha256[:len(basename)]
    assert zfs_exists_snapshot_sha256(sha256)
    assert zfs_parse_output(['zfs', 'get', '-H', 'rdonly', name])[0][2] == 'on'
    subprocess.check_output(['zfs', 'destroy', '-r', '-f', name])


def test_bootstrap_02():
    subprocess.check_output(['focker', 'image', 'remove', '--force', 'test-focker-bootstrap'])
    args = lambda: 0
    args.no_image = False
    args.empty = True
    args.unfinalized = False
    args.non_interactive = False
    args.create_interface = False
    args.full_auto = False
    args.add_pf_rule = False
    args.tags = ['test-focker-bootstrap']
    command_bootstrap(args)
    focker_unlock()
    name, sha256 = zfs_find('test-focker-bootstrap', focker_type='image')
    basename = os.path.basename(name)
    assert 7 <= len(basename) <= 64
    assert re.search('[a-f]', basename[:7])
    assert len(sha256) == 64
    assert basename == sha256[:len(basename)]
    assert zfs_exists_snapshot_sha256(sha256)
    assert zfs_parse_output(['zfs', 'get', '-H', 'rdonly', name])[0][2] == 'on'
    subprocess.check_output(['zfs', 'destroy', '-r', '-f', name])


def test_bootstrap_03():
    for a, b, c in [ (1, 1, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1) ]:
        args = lambda: 0
        args.no_image, args.empty, args.non_interactive = a, b, c
        with pytest.raises(ValueError) as excinfo:
            command_bootstrap(args)
        assert excinfo.value.args == \
            ('--no-image, --empty and --non-interactive are mutually exclusive',)


def test_bootstrap_04():
    args = lambda: 0
    args.no_image = 1
    args.unfinalized = 1
    args.empty = 0
    args.non_interactive = 0
    with pytest.raises(ValueError) as excinfo:
        command_bootstrap(args)
    assert excinfo.value.args == ('--no-image and --unfinalized are mutually exclusive',)


def test_bootstrap_05(monkeypatch):
    def fake_create_interface(args):
        raise RuntimeError('fake_create_interface called')
    monkeypatch.setattr(focker.bootstrap, 'create_interface', fake_create_interface)
    args = lambda: 0
    args.no_image = args.unfinalized = args.empty = args.non_interactive = 0
    args.create_interface = 1
    args.full_auto = 0
    with pytest.raises(RuntimeError) as excinfo:
        command_bootstrap(args)
    assert excinfo.value.args == ('fake_create_interface called',)
    args.create_interface = 0
    args.full_auto = 1
    with pytest.raises(RuntimeError) as excinfo:
        command_bootstrap(args)
    assert excinfo.value.args == ('fake_create_interface called',)


def test_bootstrap_06(monkeypatch):
    def fake_add_pf_rule(args):
        raise RuntimeError('fake_add_pf_rule called')
    def fake_create_interface(args):
        pass
    monkeypatch.setattr(focker.bootstrap, 'add_pf_rule', fake_add_pf_rule)
    monkeypatch.setattr(focker.bootstrap, 'create_interface', fake_create_interface)
    args = lambda: 0
    args.no_image = args.unfinalized = args.empty = args.non_interactive = 0
    args.create_interface = args.full_auto = 0
    args.add_pf_rule = 1
    with pytest.raises(RuntimeError) as excinfo:
        command_bootstrap(args)
    assert excinfo.value.args == ('fake_add_pf_rule called',)
    args.full_auto = 1
    args.add_pf_rule = 0
    with pytest.raises(RuntimeError) as excinfo:
        command_bootstrap(args)
    assert excinfo.value.args == ('fake_add_pf_rule called',)


def test_bootstrap_07(monkeypatch):
    def fake_add_pf_rule(args):
        pass
    def fake_create_interface(args):
        pass
    def fake_bootstrap_interactive(args):
        raise RuntimeError('fake_bootstrap_interactive called')
    def fake_bootstrap_non_interactive(args):
        raise RuntimeError('fake_bootstrap_non_interactive called')
    def fake_bootstrap_empty(args):
        raise RuntimeError('fake_bootstrap_empty called')
    # def fake_print(*args):
    #     raise RuntimeError('fake_print_called', args)
    monkeypatch.setattr(focker.bootstrap, 'add_pf_rule', fake_add_pf_rule)
    monkeypatch.setattr(focker.bootstrap, 'create_interface', fake_create_interface)
    monkeypatch.setattr(focker.bootstrap, 'bootstrap_interactive', fake_bootstrap_interactive)
    monkeypatch.setattr(focker.bootstrap, 'bootstrap_non_interactive', fake_bootstrap_non_interactive)
    monkeypatch.setattr(focker.bootstrap, 'bootstrap_empty', fake_bootstrap_empty)
    args = lambda: 0
    args.no_image = args.unfinalized = args.empty = args.non_interactive = 0
    args.create_interface = args.full_auto = args.add_pf_rule = 0
    with pytest.raises(RuntimeError) as excinfo:
        command_bootstrap(args)
    assert excinfo.value.args == ('fake_bootstrap_interactive called',)
    args.non_interactive = 1
    with pytest.raises(RuntimeError) as excinfo:
        command_bootstrap(args)
    assert excinfo.value.args == ('fake_bootstrap_non_interactive called',)
    args.non_interactive = 0
    args.empty = 1
    with pytest.raises(RuntimeError) as excinfo:
        command_bootstrap(args)
    assert excinfo.value.args == ('fake_bootstrap_empty called',)
    args.empty = 0
    args.no_image = 1
    # monkeypatch.setattr(focker.bootstrap, 'print', fake_print)
    # with pytest.raises(RuntimeError) as excinfo:
    command_bootstrap(args)
    # assert excinfo.value.args[1] == ['Image creation disabled']


def test_bootstrap_empty_01():
    args = lambda: 0
    args.tags = ['test-bootstrap-empty-01']
    args.unfinalized = False
    bootstrap_empty(args)
    name, _ = zfs_find('test-bootstrap-empty-01')
    zfs_run(['zfs', 'destroy', '-R', '-f', name])


def test_bootstrap_common_01(monkeypatch):
    args = lambda: 0
    args.tags = ['test-bootstrap-common-01']
    fake_hashlib = lambda: 0
    def fake_sha256(data):
        return hashlib.sha256('fake_sha256'.encode('utf-8'))
    fake_hashlib.sha256 = fake_sha256
    monkeypatch.setattr(focker.bootstrap, 'hashlib', fake_hashlib)
    _bootstrap_common(args)
    name, _ = zfs_find('test-bootstrap-common-01')
    zfs_run(['zfs', 'destroy', '-f', name])
