from .process import focker_subprocess_check_output, \
    focker_subprocess_run
from typing import Dict, \
    Tuple
import subprocess
import io
import csv
import yaml
import os
from functools import reduce
import random


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
        raise ValueError('Not a ZFS root')
    poolname = poolname[0][0].split('/')[0]
    return poolname


ROOT_DATASET = None
ROOT_MOUNTPOINT = None


def zfs_load_config():
    global ROOT_DATASET
    global ROOT_MOUNTPOINT
    res = None
    for p in [ os.path.expanduser('~/.focker/focker.conf'),
        '/usr/local/etc/focker/focker.conf', '/etc/focker/focker.conf' ]:
        if os.path.exists(p):
            with open(p) as f:
                data = yaml.safe_load(f)
            ROOT_DATASET = data.get('root_dataset', None)
            ROOT_MOUNTPOINT = data.get('root_mountpoint', None)
            break
    if 'FOCKER_ROOT_DATASET' in os.environ:
        ROOT_DATASET = os.environ['FOCKER_ROOT_DATASET']
    if 'FOCKER_ROOT_MOUNTPOINT' is os.environ:
        ROOT_MOUNTPOINT = os.environ['FOCKER_ROOT_MOUNTPOINT']
    if ROOT_DATASET is None:
        ROOT_DATASET = zfs_poolname() + '/focker'
    if ROOT_MOUNTPOINT is None:
        ROOT_MOUNTPOINT = '/focker'

zfs_load_config()


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
    props = reduce(list.__add__, props)
    cmd = [ 'zfs', 'create', *props, name ]
    # print('cmd:', cmd)
    focker_subprocess_run(cmd)


def zfs_init():
    for path in ['images', 'volumes', 'jails']:
        os.makedirs(os.path.join(ROOT_MOUNTPOINT, path), exist_ok=True)
    os.chmod(ROOT_MOUNTPOINT, 0o600)
    zfs_create(ROOT_DATASET, dict(canmount='off', mountpoint=ROOT_MOUNTPOINT), exist_ok=True)
    zfs_create(ROOT_DATASET + '/images', dict(canmount='off'), exist_ok=True)
    zfs_create(ROOT_DATASET + '/volumes', dict(canmount='off'), exist_ok=True)
    zfs_create(ROOT_DATASET + '/jails', dict(canmount='off'), exist_ok=True)

    #if not zfs_exists(poolname + '/focker'):
    #    zfs_run(['zfs', 'create', '-o', 'canmount=off', '-o', 'mountpoint=/focker', poolname + '/focker'])
    #if not zfs_exists(poolname + '/focker/images'):
    #    zfs_run(['zfs', 'create', '-o', 'canmount=off', poolname + '/focker/images'])
    #if not zfs_exists(poolname + '/focker/volumes'):
    #    zfs_run(['zfs', 'create', '-o', 'canmount=off', poolname + '/focker/volumes'])
    #if not zfs_exists(poolname + '/focker/jails'):
    #    zfs_run(['zfs', 'create', '-o', 'canmount=off', poolname + '/focker/jails'])


def zfs_list(fields=['name'], focker_type='image', zfs_type='filesystem'):
    fields.append('focker:sha256')
    lst = zfs_parse_output(['zfs', 'list', '-o', ','.join(fields),
        '-H', '-t', zfs_type, '-r', ROOT_DATASET + '/' + focker_type + 's'])
    lst = list(filter(lambda a: a[-1] != '-', lst))
    return lst


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
    lst = zfs_parse_output(['zfs', 'list', '-o', 'name,focker:tags', '-H', '-r', ROOT_DATASET + '/' + focker_type + 's'])
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
    for pre in range(7, len(tail)):
        name = head + tail[:pre]
        if not zfs_exists(name):
            break
    return name


def zfs_shortest_unique_name(name: str, focker_type: str) -> str:
    head = f'{ROOT_DATASET}/{focker_type}s/'
    return zfs_find_prefix(head, name)


def zfs_random_name(focker_type: str) -> str:
    return zfs_shortest_unique_name(random_sha256_hexdigest(), focker_type)


def random_sha256_hexdigest():
    for _ in range(10**6):
        res = bytes([ random.randint(0, 255) for _ in range(32) ]).hex()
        if not res[:7].isnumeric():
            return res
    raise ValueError('Couldn\'t find random SHA256 hash with non-numeric 7-character prefix in 10^6 trials o_O')


def zfs_prune(focker_type='image'):
    again = True
    while again:
        again = False
        lst = zfs_parse_output(['zfs', 'list', '-o', 'focker:sha256,focker:tags,origin,name,focker:protect', '-H', '-r', ROOT_DATASET + '/' + focker_type + 's'])
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


def zfs_set_props(name, props):
    for (k, v) in props.items():
        zfs_run(['zfs', 'set', k + '=' + v, name])
