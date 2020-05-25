import subprocess
from focker.zfs import *
import re


def test_bootstrap():
    subprocess.run(['focker', 'image', 'remove', '--force', 'test-focker-bootstrap'])
    subprocess.run(['focker', 'bootstrap', '--tags', 'test-focker-bootstrap'])
    name, sha256 = zfs_find('test-focker-bootstrap', focker_type='volume')
    assert len(name) >= 7
    assert re.search('[a-f]', name[:7])
    assert len(sha256) == 64
    assert name == sha256[:len(name)]
