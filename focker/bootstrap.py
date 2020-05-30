import subprocess
import hashlib
from .misc import find_prefix
from .zfs import zfs_poolname, \
    zfs_mountpoint, \
    zfs_tag


def command_bootstrap(args):
    version = subprocess.check_output(['freebsd-version']).decode('utf-8')
    print('FreeBSD version:', version)
    tags = args.tags or [ 'freebsd-' + version.split('-')[0], 'freebsd-latest' ]
    sha256 = hashlib.sha256(('FreeBSD ' + version).encode('utf-8')).hexdigest()
    poolname = zfs_poolname()
    name = find_prefix(poolname + '/focker/images/', sha256)
    subprocess.check_output(['zfs', 'create', '-o', 'focker:sha256=' + sha256, name])
    zfs_tag(name, tags)
    if not args.empty:
        res = subprocess.run(['bsdinstall', 'jail', zfs_mountpoint(name)])
        if res.returncode != 0:
            zfs_run(['zfs', 'destroy', '-r', '-f', name])
            raise ValueError('bsdinstall failed')
    subprocess.check_output(['zfs', 'set', 'rdonly=on', name])
    subprocess.check_output(['zfs', 'snapshot', name + '@1'])
