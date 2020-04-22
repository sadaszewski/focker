import subprocess
import csv
import io


def zfs_run(command):
    out = subprocess.check_output(command)
    return out


def zfs_parse_output(command):
    out = zfs_run(command)
    s = io.StringIO(out.decode('utf-8'))
    r = csv.reader(s, delimiter='\t')
    return [a for a in r]


def zfs_get_type(name):
    lst = zfs_parse_output(['zfs', 'list', '-o', 'name,type', '-H', name])
    return lst[0][1]


def zfs_snapshot_by_tag_or_name(s):
    lst = zfs_parse_output(['zfs', 'list', '-o', 'name,focker:tags,type', '-H'])
    lst = list(filter(lambda a: (a[0] == s or s in a[1].split(' ') and a[2] == 'snapshot')))
    if len(lst) == 0:
        raise ValueError('Reference not found: ' + s)
    if len(lst) > 1:
        raise ValueError('Ambiguous reference: ' + s)
    return lst[0][0]


def zfs_clone(name, target_name):
    zfs_run(['zfs', 'clone', name, target_name])
