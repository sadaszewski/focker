from .zfs import *


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
    base = spec.base
    base = zfs_snapshot_by_tag_or_name(base)

    root = '/'.join(base.split('/')[:-1])
    print('base:', base, 'root:', root)
