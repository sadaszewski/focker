#
# Copyright (C) Stanislaw Adaszewski, 2020
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#

from ctypes import Structure, \
    c_uint32, \
    c_uint64, \
    c_int64, \
    c_int, \
    c_char, \
    CDLL, \
    POINTER, \
    ARRAY, \
    byref
from ctypes.util import find_library
import re

with open('/usr/include/sys/mount.h', 'r') as f:
    rx = re.compile('[ \t]')
    lines = f.read().split('\n')
    lines = [ a.strip() for a in lines \
        if list(filter(lambda b: b, rx.split(a))) [:2] == \
            [ '#define', 'MNAMELEN'] ]
    MNAMELEN = int(rx.split(lines[0])[2])
    # print('MNAMELEN:', MNAMELEN)
    #line = list(filter(lambda a: \
    #    list(filter(lambda b: b, rx.split(a), a)[:2]) == \
    #        ['#define', 'MNAMELEN'], f.read().split('\n')))
    #line[0]

MFSNAMELEN = 16
# MNAMELEN = 1024


class statfs(Structure):
    pass


statfs._fields_ = [
    ('f_version', c_uint32),
    ('f_type', c_uint32),
    ('f_flags', c_uint64),
    ('f_bsize', c_uint64),
    ('f_iosize', c_uint64),
    ('f_blocks', c_uint64),
    ('f_bfree', c_uint64),
    ('f_bavail', c_int64),
    ('f_files', c_uint64),
    ('f_ffree', c_int64),
    ('f_syncwrites', c_uint64),
    ('f_asyncwrites', c_uint64),
    ('f_syncreads', c_uint64),
    ('f_asyncreads', c_uint64),
    ('f_spare', ARRAY(c_uint64, 10)),
    ('f_namemax', c_uint32),
    ('f_owner', c_uint32),
    ('f_fsid', ARRAY(c_uint32, 2)),
    ('f_charspare', ARRAY(c_char, 80)),
    ('f_fstypename', ARRAY(c_char, MFSNAMELEN)),
    ('f_mntfromname', ARRAY(c_char, MNAMELEN)),
    ('f_mntonname', ARRAY(c_char, MNAMELEN))
]

libc = CDLL(find_library('c'))

def getdict(struct):
    return dict((field, getattr(struct, field)) for field, _ in struct._fields_)

_getmntinfo = libc.getmntinfo
_getmntinfo.argtypes = [ POINTER(POINTER(statfs)), c_int ]

def getmntinfo():
    p = POINTER(statfs)()
    n = _getmntinfo(byref(p), c_int(1))
    res = [ getdict(p[i]) for i in range(n) ]
    return res
