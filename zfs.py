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
