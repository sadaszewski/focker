import subprocess
from focker.zfs import *
import re
import os


def test_bootstrap():
    subprocess.run(['focker', 'image', 'remove', '--force', 'test-focker-bootstrap'])
    subprocess.run(['focker', 'bootstrap', '--dry-run', '--tags', 'test-focker-bootstrap'])
    name, sha256 = zfs_find('test-focker-bootstrap', focker_type='image')
    basename = os.path.basename(name)
    assert len(basename) >= 7
    assert re.search('[a-f]', basename[:7])
    assert len(sha256) == 64
    assert basename == sha256[:len(basename)]
    assert zfs_exists_snapshot_sha256(sha256)
    subprocess.check_output(['zfs', 'destroy', '-r', '-f', name])
