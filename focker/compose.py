#
# Copyright (C) Stanislaw Adaszewski, 2020
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#

import os
import yaml
from .zfs import AmbiguousValueError, \
    zfs_find, \
    zfs_tag, \
    zfs_untag, \
    zfs_mountpoint
from .jail import jail_fs_create, \
    jail_create, \
    jail_remove
from .misc import random_sha256_hexdigest, \
    find_prefix
import subprocess
import jailconf
import os


def build_volumes(spec):
    for tag in spec.keys():
        try:
            name, _ = zfs_find(tag, focker_type='volume')
            continue
        except AmbiguousValueError:
            raise
        except ValueError:
            pass
        sha256 = random_sha256_hexdigest()
        name = find_prefix(poolname + '/focker/volumes/', sha256)
        subprocess.check_output(['zfs', 'create', name])
        zfs_untag([ tag ], focker_type='volume')
        zfs_tag(name, [ tag ])


def build_images(spec, path):
    # print('build_images(): NotImplementedError')
    for (tag, focker_dir) in spec.items():
        res = subprocess.run(['focker', 'image', 'build',
            os.path.join(path, focker_dir), '-t', tag])
        if res.returncode != 0:
            raise RuntimeError('Image build failed: ' + str(res.returncode))


def build_jails(spec):
    #if os.path.exists('/etc/jail.conf'):
    #    conf = jailconf.load('/etc/jail.conf')
    #else:
    #    conf = jailconf.JailConf()
    for (jailname, jailspec) in spec.items():
        try:
            name, _ = zfs_find(jailname, focker_type='jail')
            jail_remove(zfs_mountpoint(name))
        except AmbiguousValueError:
            raise
        except ValueError:
            pass
        name = jail_fs_create(jailspec['image'])
        zfs_untag([ jailname ], focker_type='jail')
        zfs_tag(name, [ jailname ])
        path = zfs_mountpoint(name)
        jail_create(path,
            jailspec.get('exec.start', '/bin/sh /etc/rc'),
            jailspec.get('env', {}),
            [ [from_, on] \
                for (from_, on) in jailspec.get('mounts', {}).items() ],
            hostname=jailname,
            overrides={
                'exec.stop': jailspec.get('exec.stop', '/bin/sh /etc/rc.shutdown'),
                'ip4.addr': jailspec.get('ip4.addr', '127.0.1.0'),
                'interface': jailspec.get('interface', 'lo1')
            })


def command_compose_build(args):
    if not os.path.exists(args.filename):
        raise ValueError('File not found: ' + args.filename)
    path, _ = os.path.split(args.filename)
    with open(args.filename, 'r') as f:
        spec = yaml.safe_load(f)
    if 'volumes' in spec:
        build_volumes(spec['volumes'])
    if 'images' in spec:
        build_images(spec['images'], path)
    if 'jails' in spec:
        build_jails(spec['jails'])



def command_compose_run(args):
    raise NotImplementedError
