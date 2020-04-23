from .zfs import *
import os
import yaml
from .steps import create_step
from .snapshot import new_snapshot


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
        raise ValueError('Missing base in specification')

    if 'steps' not in spec:
        raise ValueError('Missing steps in specification')

    base = spec['base']
    base, base_sha256 = zfs_snapshot_by_tag_or_sha256(base)

    root = '/'.join(base.split('/')[:-1])
    print('base:', base, 'root:', root)

    steps = spec['steps']
    if not isinstance(steps, list):
        steps = [ steps ]

    for st in steps:
        st = create_step(st)
        st_sha256 = st.hash(base_sha256)
        if zfs_exists_snapshot_sha256(st_sha256):
            base = zfs_snapshot_by_sha256(st_sha256)
            base_sha256 = st_sha256
            print('Reusing:', base)
            continue
        for pre in range(7, 64):
            name = root + '/' + st_sha256[:pre]
            if not zfs_exists(name):
                break
        snap_name = new_snapshot(base, lambda: st.execute(zfs_mountpoint(name)), name)
        feed = {
            'focker:sha256': st_sha256
        }
        zfs_set_props(name, feed)
        # zfs_set_props(snap_name, feed)
        base = snap_name
        base_sha256 = st_sha256

    return (base, base_sha256)


def command_image_build(args):
    fname = os.path.join(args.focker_dir, 'Fockerfile')
    print('fname:', fname)
    if not os.path.exists(fname):
        raise ValueError('No Fockerfile could be found in the specified directory')
    with open(fname, 'r') as f:
        spec = yaml.safe_load(f)
    print('spec:', spec)
    image, image_sha256 = build(spec)
    zfs_untag(args.tag)
    zfs_tag(image.split('@')[0], args.tag)

def command_image_untag(args):
    zfs_untag(args.tags)
