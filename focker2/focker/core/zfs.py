from .process import focker_subprocess_check_output
from typing import Dict, \
    Tuple
import subprocess
import io
import csv


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


def zfs_list(fields=['name'], focker_type='image', zfs_type='filesystem'):
    poolname = zfs_poolname()
    fields.append('focker:sha256')
    lst = zfs_parse_output(['zfs', 'list', '-o', ','.join(fields),
        '-H', '-t', zfs_type, '-r', poolname + '/focker/' + focker_type + 's'])
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
    poolname = zfs_poolname()
    lst = zfs_parse_output(['zfs', 'list', '-o', 'name,focker:tags', '-H', '-r', poolname + '/focker/' + focker_type + 's'])
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


def zfs_shortest_unique_name(name: str, focker_type: str) -> str:
    poolname = zfs_poolname()
    head = f'{poolname}/focker/{focker_type}s/'
    return find_prefix(head, name)
