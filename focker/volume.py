#
# Copyright (C) Stanislaw Adaszewski, 2020
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#

from .misc import random_sha256_hexdigest
from .zfs import *
from tabulate import tabulate


def command_volume_create(args):
    sha256 = random_sha256_hexdigest()
    poolname = zfs_poolname()
    for pre in range(7, 64):
        name = poolname + '/focker/volumes/' + sha256[:pre]
        if not zfs_exists(name):
            break
    zfs_run(['zfs', 'create', '-o', 'focker:sha256=' + sha256, name])
    zfs_untag(args.tags, focker_type='volume')
    zfs_tag(name, args.tags)


def command_volume_prune(args):
    zfs_prune(focker_type='volume')


def command_volume_list(args):
    poolname = zfs_poolname()
    lst = zfs_parse_output(['zfs', 'list', '-o', 'name,refer,focker:sha256,focker:tags,mountpoint', '-H', '-r', poolname + '/focker/volumes'])
    lst = list(filter(lambda a: a[2] != '-', lst))
    lst = list(map(lambda a: [ a[3], a[1],
        a[2] if args.full_sha256 else a[2][:7],
        a[4] ], lst))
    print(tabulate(lst, headers=['Tags', 'Size', 'SHA256', 'Mountpoint']))


def command_volume_tag(args):
    name, _ = zfs_find(args.reference, focker_type='volume')
    zfs_untag(args.tags, focker_type='volume')
    zfs_tag(name, args.tags)


def command_volume_untag(args):
    zfs_untag(args.tags, focker_type='volume')
