import os
import yaml
from .zfs import AmbiguousValueError, \
    zfs_find, \
    zfs_tag
from .misc import random_sha256_hexdigest, \
    find_prefix
import subprocess


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
    print('build_jails(): NotImplementedError')


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
