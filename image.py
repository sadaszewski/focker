from .zfs import *
import os
import yaml


def process_step(step, name):
    cmd=['jail', '-c']
    cmd.append('path=' + '/focker/' + name)


def process_steps(steps, name):
    if isinstance(steps, list):
        for step in steps:
            process_step(step, name)
    else:
        process_step(steps, name)


def build(spec):
    if 'base' not in spec:
        raise ValueError('Missing base specification')
    base = spec['base']
    base = zfs_snapshot_by_tag_or_sha256(base)

    root = '/'.join(base.split('/')[:-1])
    print('base:', base, 'root:', root)


def command_image_build(args):
    fname = os.path.join(args.focker_dir, 'Fockerfile')
    print('fname:', fname)
    if not os.path.exists(fname):
        raise ValueError('No Fockerfile could be found in the specified directory')
    with open(fname, 'r') as f:
        spec = yaml.safe_load(f)
    print('spec:', spec)
    build(spec)
