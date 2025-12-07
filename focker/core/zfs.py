#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from .process import focker_subprocess_check_output, \
    focker_subprocess_run
from typing import Dict, \
    Tuple
import subprocess
import io
import csv
import os
from functools import reduce
import random
from collections import defaultdict


def zfs_run(command):
    out = focker_subprocess_check_output(command, stderr=subprocess.STDOUT)
    return out


def zfs_parse_output(command):
    out = focker_subprocess_check_output(command, stderr=subprocess.STDOUT)
    s = io.StringIO(out.decode('utf-8'))
    r = csv.reader(s, delimiter='\t')
    return [ a for a in r ]


def zfs_poolname():
    poolname = zfs_parse_output(['zfs', 'list', '-H', '/'])
    if len(poolname) == 0:
        raise RuntimeError('The root filesystem is not ZFS')
    poolname = poolname[0][0].split('/')[0]
    return poolname


def zfs_exists(name):
    try:
        zfs_run(['zfs', 'list', name])
    except subprocess.CalledProcessError as e:
        return False
    return True


def zfs_create(name, props={}, exist_ok=False):
    if zfs_exists(name):
        if exist_ok:
            return
        else:
            raise RuntimeError('Specified ZFS dataset already exists')
    props = [ [ '-o', f'{k}={v}' ] for k, v in props.items() ]
    props = reduce(list.__add__, props, [])
    cmd = [ 'zfs', 'create', *props, name ]
    # print('cmd:', cmd)
    focker_subprocess_run(cmd)


def zfs_init():
    from .config import FOCKER_CONFIG
    for path in ['images', 'volumes', 'jails']:
        os.makedirs(os.path.join(FOCKER_CONFIG.zfs.root_mountpoint, path), exist_ok=True)
    os.chmod(FOCKER_CONFIG.zfs.root_mountpoint, 0o600)
    zfs_create(FOCKER_CONFIG.zfs.root_dataset, dict(canmount='off', mountpoint=FOCKER_CONFIG.zfs.root_mountpoint), exist_ok=True)
    zfs_create(FOCKER_CONFIG.zfs.root_dataset + '/images', dict(canmount='off'), exist_ok=True)
    zfs_create(FOCKER_CONFIG.zfs.root_dataset + '/volumes', dict(canmount='off'), exist_ok=True)
    zfs_create(FOCKER_CONFIG.zfs.root_dataset + '/jails', dict(canmount='off'), exist_ok=True)
    zfs_create(FOCKER_CONFIG.zfs.root_dataset + '/jailconf', exist_ok=True)


def zfs_list(fields=['name'], focker_type='image', zfs_type='filesystem'):
    from .config import FOCKER_CONFIG
    fields = list(fields)
    fields.append('focker:sha256')
    lst = zfs_parse_output(['zfs', 'list', '-o', ','.join(fields),
        '-H', '-t', zfs_type, '-r', FOCKER_CONFIG.zfs.root_dataset + '/' + focker_type + 's'])
    lst = list(filter(lambda a: a[-1] != '-', lst))
    return lst


def zfs_tag(name, tags, replace=False):
    if any(' ' in a for a in tags):
        raise ValueError('Tags cannot contain spaces')
    if any(a == '-' for a in tags):
        raise ValueError('Tags cannot consist of just the minus sign')
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
    from .config import FOCKER_CONFIG
    if any(map(lambda a: ' ' in a, tags)):
        raise ValueError('Tags cannot contain spaces')
    # print('zfs_untag(), tags:', tags)
    lst = zfs_parse_output(['zfs', 'list', '-o', 'name,focker:tags', '-H', '-r',
        FOCKER_CONFIG.zfs.root_dataset + '/' + focker_type + 's'])
    lst = filter(lambda a: any([b in a[1].split(' ') for b in tags]), lst)
    for row in lst:
        cur_tags = row[1].split(' ')
        for t in tags:
            if t in cur_tags:
                cur_tags.remove(t)
        zfs_tag(row[0], cur_tags, replace=True)


def zfs_destroy(name):
    lst = zfs_parse_output(['zfs', 'get', '-H', 'focker:protect', name])
    if lst[0][2] != '-':
        raise RuntimeError('%s is protected against removal' % name)
    zfs_run(['zfs', 'destroy', '-r', '-f', name])


def zfs_protect(name):
    zfs_run(['zfs', 'set', 'focker:protect=on', name])


def zfs_unprotect(name):
    zfs_run(['zfs', 'inherit', '-r', 'focker:protect', name])


def zfs_get_property(name, prop_name):
    lst = zfs_parse_output([ 'zfs', 'get', '-H', prop_name, name ])
    assert len(lst) == 1
    return lst[0][2]


def zfs_clone(name, target_name, props={}):
    cmd = [ 'zfs', 'clone' ]
    for k, v in props.items():
        cmd.append('-o')
        cmd.append(f'{k}={v}')
    cmd += [ name, target_name ]
    zfs_run(cmd)


def zfs_mountpoint(name):
    lst = zfs_parse_output(['zfs', 'list', '-o', 'mountpoint', '-H', name])
    return lst[0][0]


def zfs_find_props(props: Dict[str, str], focker_type: str, zfs_type: str) -> Tuple[list, list]:
    pkeys = list(props.keys())
    pvals = [ props[k] for k in pkeys ]
    n_props = len(props)
    lst = zfs_list(pkeys, focker_type=focker_type,
        zfs_type=zfs_type)
    lst = [ e for e in lst if all([ e[i] == pvals[i] for i in range(n_props) ]) ]
    return lst, pkeys


def zfs_exists_props(props: Dict[str, str], focker_type: str, zfs_type: str) -> bool:
    lst, _ = zfs_find_props(props, focker_type, zfs_type)
    return ( len(lst) > 0 )


def zfs_find_prefix(head, tail):
    assert len(tail) > 7
    for pre in range(7, len(tail) + 1):
        name = head + tail[:pre]
        if not zfs_exists(name):
            break
    return name


def zfs_shortest_unique_name(name: str, focker_type: str) -> str:
    from .config import FOCKER_CONFIG
    head = f'{FOCKER_CONFIG.zfs.root_dataset}/{focker_type}s/'
    return zfs_find_prefix(head, name)


def random_sha256_hexdigest():
    for _ in range(10**6):
        res = bytes([ random.randint(0, 255) for _ in range(32) ]).hex()
        if not res[:7].isnumeric():
            return res
    raise ValueError('Couldn\'t find random SHA256 hash with non-numeric 7-character prefix in 10^6 trials o_O') # pragma: no cover


def zfs_set_props(name, props):
    for (k, v) in props.items():
        zfs_run(['zfs', 'set', k + '=' + v, name])


def zfs_snapshot(name):
    zfs_run(['zfs', 'snapshot', name])


def zfs_rollback(name, force=False):
    if force:
        zfs_run(['zfs', 'rollback', '-r', name])
    else:
        zfs_run(['zfs', 'rollback', name])


def zfs_properties_cache(focker_type: str = None):
    from .config import FOCKER_CONFIG
    cmd = [ 'zfs', 'get', '-r', '-H', 'all' ]
    if focker_type is not None:
        cmd.append(f'{FOCKER_CONFIG.zfs.root_dataset}/{focker_type}s')
    lst = zfs_parse_output(cmd)
    res = defaultdict(lambda: {})
    for (name, propname, propvalue, *_) in lst:
        res[name][propname] = propvalue
    return res
