#
# Copyright (C) Stanislaw Adaszewski, 2020
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#

from .zfs import *
import os
import yaml
from .steps import create_step
from .snapshot import new_snapshot
from tabulate import tabulate
import subprocess


def build(spec, args):
    if 'base' not in spec:
        raise ValueError('Missing base in specification')

    if 'steps' not in spec:
        raise ValueError('Missing steps in specification')

    base = spec['base']
    base, base_sha256 = zfs_find(base, focker_type='image', zfs_type='snapshot')

    root = '/'.join(base.split('/')[:-1])
    print('base:', base, 'root:', root)

    steps = spec['steps']
    if not isinstance(steps, list):
        steps = [ steps ]

    for st in steps:
        st = create_step(st)
        st_sha256 = st.hash(base_sha256, args=args)
        if zfs_exists_snapshot_sha256(st_sha256):
            base = zfs_snapshot_by_sha256(st_sha256)
            base_sha256 = st_sha256
            print('Reusing:', base)
            continue
        for pre in range(7, 64):
            name = root + '/' + st_sha256[:pre]
            if not zfs_exists(name):
                break
        feed = {
            'focker:sha256': st_sha256
        }
        def atomic():
            st.execute(zfs_mountpoint(name), args=args)
            zfs_set_props(name, feed)
        snap_name = new_snapshot(base, atomic, name)
        # zfs_set_props(name, feed)
        # zfs_set_props(snap_name, feed)
        base = snap_name
        base_sha256 = st_sha256

    return (base, base_sha256)


def command_image_build(args):
    # os.chdir(args.focker_dir)
    fname = os.path.join(args.focker_dir, 'Fockerfile')
    print('fname:', fname)
    if not os.path.exists(fname):
        raise ValueError('No Fockerfile could be found in the specified directory')
    with open(fname, 'r') as f:
        spec = yaml.safe_load(f)
    print('spec:', spec)
    image, image_sha256 = build(spec, args)
    zfs_untag(args.tags)
    zfs_tag(image.split('@')[0], args.tags)


def command_image_tag(args):
    zfs_untag(args.tags, focker_type='image')
    name, _ = zfs_find(args.reference, focker_type='image', zfs_type='filesystem')
    zfs_tag(name, args.tags)


def command_image_untag(args):
    zfs_untag(args.tags, focker_type='image')


def command_image_list(args):
    lst = zfs_list(fields=['name', 'refer', 'focker:sha256', 'focker:tags', 'origin'],
        focker_type='image')
    # zfs_parse_output(['zfs', 'list', '-o', 'name,refer,focker:sha256,focker:tags,origin', '-H'])
    lst = list(filter(lambda a: a[2] != '-', lst))
    lst = list(map(lambda a: [ a[3], a[1],
        a[2] if args.full_sha256 else a[2][:7],
        a[4].split('/')[-1].split('@')[0] ], lst))
    print(tabulate(lst, headers=['Tags', 'Size', 'SHA256', 'Base']))


def command_image_prune(args):
    poolname = zfs_poolname()
    again = True
    while again:
        again = False
        lst = zfs_list(fields=['focker:sha256', 'focker:tags', 'origin', 'name'],
            focker_type='image')
        # lst = zfs_parse_output(['zfs', 'list', '-o', 'focker:sha256,focker:tags,origin,name', '-H', '-r', poolname + '/focker/images'])
        used = set()
        for r in lst:
            if r[2] == '-':
                continue
            used.add(r[2].split('@')[0])
        for r in lst:
            if r[0] == '-' or r[1] != '-':
                continue
            if r[3] not in used:
                print('Removing:', r[3])
                zfs_run(['zfs', 'destroy', '-r', '-f', r[3]])
                again = True
    # zfs_parse_output(['zfs'])


def command_image_remove(args):
    snap, snap_sha256 = zfs_find(args.reference, focker_type='image',
        zfs_type='snapshot')
    ds = snap.split('@')[0]
    command = ['zfs', 'destroy', '-r', '-f']
    #if args.remove_children:
    #    command.append('-r')
    if args.remove_dependents:
        command.append('-R')
    command.append(ds)
    subprocess.run(command)
    # zfs_run(['zfs', 'destroy', ds])
