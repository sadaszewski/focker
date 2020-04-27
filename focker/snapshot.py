from .zfs import *


def new_snapshot(base, fun, name):
    type_ = zfs_get_type(base)
    if type_ != 'snapshot':
        raise ValueError('Provided base dataset is not a snapshot')
    if '/' not in name:
        root = '/'.join(base.split('/')[:-1])
        name = root + '/' + name
    zfs_run(['zfs', 'clone', base, name])
    try:
        fun()
        zfs_run(['zfs', 'set', 'readonly=on', name])
        snap_name = name + '@1'
        zfs_run(['zfs', 'snapshot', snap_name])
    except:
        zfs_run(['zfs', 'destroy', '-f', name])
        raise
    return snap_name
