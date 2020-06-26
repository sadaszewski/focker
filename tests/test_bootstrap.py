import subprocess
from focker.zfs import *
import re
import os
from focker.bootstrap import command_bootstrap
from focker.misc import focker_unlock


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
