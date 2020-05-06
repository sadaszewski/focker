#
# Copyright (C) Stanislaw Adaszewski, 2020
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#

from .zfs import *
from .misc import focker_lock, \
    focker_unlock


def new_snapshot(base, fun, name):
    type_ = zfs_get_type(base)
    if type_ != 'snapshot':
        raise ValueError('Provided base dataset is not a snapshot')
    if '/' not in name:
        root = '/'.join(base.split('/')[:-1])
        name = root + '/' + name
    zfs_run(['zfs', 'clone', base, name])
    try:
        try:
            focker_unlock()
            fun()
        finally:
            focker_lock()
        zfs_run(['zfs', 'set', 'readonly=on', name])
        snap_name = name + '@1'
        zfs_run(['zfs', 'snapshot', snap_name])
    except:
        zfs_run(['zfs', 'destroy', '-f', name])
        raise
    return snap_name
