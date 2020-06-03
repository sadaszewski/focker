#
# Copyright (C) Stanislaw Adaszewski, 2020
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#

import subprocess
import csv
import io
import os


class AmbiguousValueError(ValueError):
    def __init__(self, msg):
        super().__init__(msg)


def zfs_run(command):
    # print('Running:', command)
    out = subprocess.check_output(command, stderr=subprocess.STDOUT)
    return out


def zfs_parse_output(command):
    out = zfs_run(command)
    s = io.StringIO(out.decode('utf-8'))
    r = csv.reader(s, delimiter='\t')
    return [a for a in r]


def zfs_get_type(name):
    lst = zfs_parse_output(['zfs', 'list', '-o', 'name,type', '-H', name])
    return lst[0][1]


def zfs_snapshot_by_tag_or_sha256(s, focker_type='image'):
    lst = zfs_parse_output(['zfs', 'list', '-o', 'focker:sha256,focker:tags,type,name',
        '-H', '-t', 'snapshot', '-r', poolname + '/focker/' + focker_type + 's'])
    lst = list(filter(lambda a: (a[0] == s or s in a[1].split(' ')) and a[2] == 'snapshot', lst))
    if len(lst) == 0:
        raise ValueError('Reference not found: ' + s)
    if len(lst) > 1:
        raise AmbiguousValueError('Ambiguous reference: ' + s)
    return (lst[0][3], lst[0][0])


def zfs_find(reference, focker_type='image', zfs_type='filesystem'):
    poolname = zfs_poolname()
    lst = zfs_parse_output(['zfs', 'list', '-o', 'focker:sha256,focker:tags,type,name', '-H', '-t', zfs_type, '-r', poolname + '/focker/' + focker_type + 's'])
    def match(sha256, tags, type, name, exact=False):
        if exact:
            predicate = lambda a: (a == reference)
        else:
            predicate = lambda a: a.startswith(reference)
        if predicate(sha256) or \
            any(map(predicate, tags.split(' '))) or \
            predicate(name.split('/')[-1]):
            return True
        return False
    lst = list(filter(lambda a: match(*a), lst))
    exact_lst = list(filter(lambda a: match(*a, exact=True), lst))
    if len(lst) == 0:
        raise ValueError('Reference not found: ' + reference)
    if len(lst) > 1:
        if len(exact_lst) == 1:
            return (exact_lst[0][3], exact_lst[0][0])
        raise AmbiguousValueError('Ambiguous reference: ' + reference)
    return (lst[0][3], lst[0][0])


def zfs_list(fields=['name'], focker_type='image', zfs_type='filesystem'):
    poolname = zfs_poolname()
    fields.append('focker:sha256')
    lst = zfs_parse_output(['zfs', 'list', '-o', ','.join(fields),
        '-H', '-t', zfs_type, '-r', poolname + '/focker/' + focker_type + 's'])
    lst = list(filter(lambda a: a[-1] != '-', lst))
    return lst


def zfs_prune(focker_type='image'):
    poolname = zfs_poolname()
    again = True
    while again:
        again = False
        lst = zfs_parse_output(['zfs', 'list', '-o', 'focker:sha256,focker:tags,origin,name,focker:protect', '-H', '-r', poolname + '/focker/' + focker_type + 's'])
        used = set()
        for r in lst:
            if r[2] == '-':
                continue
            used.add(r[2].split('@')[0])
        for r in lst:
            if r[0] == '-' or r[1] != '-':
                continue
            if r[3] in used:
                continue
            if r[4] != '-':
                print('%s is protected against removal' % r[3])
                continue
            print('Removing:', r[3])
            zfs_run(['zfs', 'destroy', '-r', '-f', r[3]])
            again = True


def zfs_destroy(name):
    lst = zfs_parse_output(['zfs', 'get', '-H', 'focker:protect', name])
    if lst[0][2] != '-':
        raise RuntimeError('%s is protected against removal' % name)
    zfs_run(['zfs', 'destroy', '-r', '-f', name])


def zfs_protect(name):
    zfs_run(['zfs', 'set', 'focker:protect=on', name])


def zfs_unprotect(name):
    zfs_run(['zfs', 'inherit', '-r', 'focker:protect', name])


def zfs_clone(name, target_name):
    zfs_run(['zfs', 'clone', name, target_name])


def zfs_exists(name):
    try:
        zfs_run(['zfs', 'list', name])
    except subprocess.CalledProcessError as e:
        return False
    return True


def zfs_set_props(name, props):
    for (k, v) in props.items():
        zfs_run(['zfs', 'set', k + '=' + v, name])


def zfs_mountpoint(name):
    lst = zfs_parse_output(['zfs', 'list', '-o', 'mountpoint', '-H', name])
    return lst[0][0]


def zfs_exists_snapshot_sha256(sha256, focker_type='image'):
    poolname = zfs_poolname()
    lst = zfs_parse_output(['zfs', 'list', '-o', 'focker:sha256', '-t', 'snap',
        '-r', poolname + '/focker/' + focker_type + 's'])
    lst = list(filter(lambda a: a[0] == sha256, lst))
    if len(lst) == 0:
        return False
    return True


def zfs_snapshot_by_sha256(sha256, focker_type='image'):
    poolname = zfs_poolname()
    lst = zfs_parse_output(['zfs', 'list', '-o', 'focker:sha256,name',
        '-t', 'snap', '-H', '-r', poolname + '/focker/' + focker_type + 's'])
    lst = list(filter(lambda a: a[0] == sha256, lst))
    if len(lst) == 0:
        raise ValueError('Snapshot with given sha256 does not exist: ' + sha256)
    if len(lst) > 1:
        raise AmbiguousValueError('Ambiguous snapshot sha256: ' + sha256)
    return lst[0][1]


def zfs_tag(name, tags, replace=False):
    if any(map(lambda a: ' ' in a, tags)):
        raise ValueError('Tags cannot contain spaces')
    lst = zfs_parse_output(['zfs', 'list', '-o', 'focker:tags', '-H', name])
    if not replace:
        tags = list(tags)
        tags.extend(lst[0][0].split(' '))
        tags = list(set(tags))
        tags = list(filter(lambda a: a != '-', tags))
    if len(tags) > 0:
        zfs_run(['zfs', 'set', 'focker:tags=' + ' '.join(tags), name])
    else:
        zfs_run(['zfs', 'inherit', 'focker:tags', name])


def zfs_untag(tags, focker_type='image'):
    if any(map(lambda a: ' ' in a, tags)):
        raise ValueError('Tags cannot contain spaces')
    # print('zfs_untag(), tags:', tags)
    poolname = zfs_poolname()
    lst = zfs_parse_output(['zfs', 'list', '-o', 'name,focker:tags', '-H', '-r', poolname + '/focker/' + focker_type + 's'])
    lst = filter(lambda a: any([b in a[1].split(' ') for b in tags]), lst)
    for row in lst:
        cur_tags = row[1].split(' ')
        for t in tags:
            if t in cur_tags:
                cur_tags.remove(t)
        zfs_tag(row[0], cur_tags, replace=True)


def zfs_name(path):
    lst = zfs_parse_output(['zfs', 'list', '-o', 'name', '-H', path])
    if len(lst) == 0:
        raise ValueError('Not a ZFS path')
    if len(lst) > 1:
        raise AmbiguousValueError('Ambiguous ZFS path')
    return lst[0][0]


def zfs_poolname():
    poolname = zfs_parse_output(['zfs', 'list', '-H', '/'])
    if len(poolname) == 0:
        raise ValueError('Not a ZFS root')
    poolname = poolname[0][0].split('/')[0]
    return poolname


def zfs_init():
    poolname = zfs_poolname()
    print('poolname:', poolname)
    for path in ['/focker', '/focker/images', '/focker/volumes', '/focker/jails']:
        if not os.path.exists(path):
            os.mkdir(path)
    os.chmod('/focker', 0o600)
    if not zfs_exists(poolname + '/focker'):
        zfs_run(['zfs', 'create', '-o', 'canmount=off', '-o', 'mountpoint=/focker', poolname + '/focker'])
    if not zfs_exists(poolname + '/focker/images'):
        zfs_run(['zfs', 'create', '-o', 'canmount=off', poolname + '/focker/images'])
    if not zfs_exists(poolname + '/focker/volumes'):
        zfs_run(['zfs', 'create', '-o', 'canmount=off', poolname + '/focker/volumes'])
    if not zfs_exists(poolname + '/focker/jails'):
        zfs_run(['zfs', 'create', '-o', 'canmount=off', poolname + '/focker/jails'])
