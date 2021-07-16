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
from .misc import find_prefix, \
    focker_subprocess_check_output, \
    focker_subprocess_run
from .zfs2 import zfs_find_sha256


def validate_spec(spec):
    if 'base' not in spec:
        raise ValueError('Missing base in specification')

    if ('steps' in spec) + ('facets' in spec) != 1:
        raise ValueError('Expected exactly one of "steps" or "facets" in the specification')


def process_facets(spec, args):
    spec = dict(spec)
    spec['steps'] = []
    for fnam in spec['facets']:
        fnam = os.path.join(args.focker_dir, fnam)
        with open(fnam) as f:
            facet = yaml.safe_load(f)
        if not isinstance(facet, list):
            raise RuntimeError('Facets are expected to contain a list of steps')
        spec['steps'] += facet
    del spec['facets']
    return spec


def build_squeeze(spec, args):
    validate_spec(spec)
    spec = process_facets(spec, args)

    base = spec['base']
    base, sha256 = zfs_find(base, focker_type='image', zfs_type='snapshot')

    root = '/'.join(base.split('/')[:-1])
    print('base:', base, 'root:', root)

    steps = spec['steps']
    if not isinstance(steps, list):
        steps = [ steps ]

    for st in steps:
        st = create_step(st)
        sha256 = st.hash(sha256, args=args)

    if zfs_exists_snapshot_sha256(sha256):
        name = zfs_snapshot_by_sha256(sha256)
        print('Reusing:', name)
        return (name, sha256)

    res = zfs_find_sha256(sha256, focker_type='image',
        zfs_type='filesystem')
    if res is not None:
        raise RuntimeError('A build with the same SHA256 is in progress')

    name = find_prefix(root + '/', sha256)

    def atomic():
        for st in steps:
            st = create_step(st)
            st.execute(zfs_mountpoint(name), args=args)

    props = {
        'focker:sha256': sha256
    }
    name = new_snapshot(base, atomic, name, props)

    return (name, sha256)


def build(spec, args):
    validate_spec(spec)
    spec = process_facets(spec, args)

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

        res = zfs_find_sha256(st_sha256, focker_type='image',
            zfs_type='filesystem')
        if res is not None:
            raise RuntimeError('A build with the same SHA256 is in progress')

        for pre in range(7, 64):
            name = root + '/' + st_sha256[:pre]
            if not zfs_exists(name):
                break
        props = {
            'focker:sha256': st_sha256
        }
        def atomic():
            st.execute(zfs_mountpoint(name), args=args)
        snap_name = new_snapshot(base, atomic, name, props)
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
    image, image_sha256 = build_squeeze(spec, args) \
        if args.squeeze else build(spec, args)
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
    lst = filter(lambda a: a[2] != '-', lst)
    if args.tagged_only:
        lst = filter(lambda a: a[3] != '-', lst)
    lst = list(lst)
    lst = list(map(lambda a: [ a[3], a[1],
        a[2] if args.full_sha256 else a[2][:7],
        a[4].split('/')[-1].split('@')[0] ], lst))
    print(tabulate(lst, headers=['Tags', 'Size', 'SHA256', 'Base']))


def command_image_prune(args):
    poolname = zfs_poolname()
    again = True
    while again:
        again = False
        fields=['focker:sha256', 'focker:tags', 'origin', 'name']
        lst = zfs_list(fields=fields, focker_type='image')
        lst += zfs_list(fields=fields, focker_type='jail')
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
    try:
        snap, snap_sha256 = zfs_find(args.reference, focker_type='image',
            zfs_type='snapshot')
    except AmbiguousValueError:
        raise
    except ValueError:
        if args.force:
            return
        raise
    ds = snap.split('@')[0]
    command = ['zfs', 'destroy', '-r', '-f']
    #if args.remove_children:
    #    command.append('-r')
    if args.remove_dependents:
        command.append('-R')
    command.append(ds)
    res = focker_subprocess_run(command)
    if res.returncode != 0:
        raise RuntimeError('zfs destroy failed')
    # zfs_run(['zfs', 'destroy', ds])
