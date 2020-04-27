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


MFSNAMELEN = 16
MNAMELEN = 1024


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
