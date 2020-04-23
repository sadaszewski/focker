import subprocess
import csv
import io
import os


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


def zfs_snapshot_by_tag_or_sha256(s):
    lst = zfs_parse_output(['zfs', 'list', '-o', 'focker:sha256,focker:tags,type,name', '-H', '-t', 'snapshot'])
    lst = list(filter(lambda a: (a[0] == s or s in a[1].split(' ')) and a[2] == 'snapshot', lst))
    if len(lst) == 0:
        raise ValueError('Reference not found: ' + s)
    if len(lst) > 1:
        raise ValueError('Ambiguous reference: ' + s)
    return (lst[0][3], lst[0][0])


def zfs_clone(name, target_name):
    zfs_run(['zfs', 'clone', name, target_name])


def zfs_exists(name):
    try:
        zfs_run(['zfs', 'list', name])
    except subprocess.CalledProcessError as e:
        return False
    return True


def zfs_tag(name, props):
    for (k, v) in props.items():
        zfs_run(['zfs', 'set', k + '=' + v, name])


def zfs_mountpoint(name):
    lst = zfs_parse_output(['zfs', 'list', '-o', 'mountpoint', '-H', name])
    return lst[0][0]


def zfs_init():
    poolname = zfs_parse_output(['zfs', 'list', '-H', '/'])
    if len(poolname) == 0:
        raise ValueError('Not a ZFS root')
    poolname = poolname[0][0].split('/')[0]
    print('poolname:', poolname)
    for path in ['/focker', '/focker/images', '/focker/volumes', '/focker/jails']:
        if not os.path.exists(path):
            os.mkdir(path)
    if not zfs_exists(poolname + '/focker'):
        zfs_run(['zfs', 'create', '-o', 'canmount=off', '-o', 'mountpoint=/focker', poolname + '/focker'])
    if not zfs_exists(poolname + '/focker/images'):
        zfs_run(['zfs', 'create', '-o', 'canmount=off', poolname + '/focker/images'])
    if not zfs_exists(poolname + '/focker/volumes'):
        zfs_run(['zfs', 'create', '-o', 'canmount=off', poolname + '/focker/volumes'])
    if not zfs_exists(poolname + '/focker/volumes'):
        zfs_run(['zfs', 'create', '-o', 'canmount=off', poolname + '/focker/jails'])
