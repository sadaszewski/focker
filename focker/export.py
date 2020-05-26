from tarfile import TarFile, \
    TarInfo
import os
import stat
from itertools import chain
from .misc import filehash


def normalized_recursive_directory_iterator(path):
    Q = iter([ path ])
    name = next(Q, None)
    while name:
        st = os.lstat(name)
        if stat.S_ISDIR(st.st_mode):
            L = sorted(os.listdir(name))
            def create_map(name, L):
                return map(lambda x: os.path.join(name, x), L)
            L = create_map(name, L)
            yield (os.path.relpath(name, path), name, st.st_mode, st.st_uid, st.st_gid, st.st_size)
            Q = chain(L, Q)
        else: # file
            yield (os.path.relpath(name, path), name, st.st_mode, st.st_uid, st.st_gid, st.st_size)
        name = next(Q, None)


def _export_diff(mountpoint, origin_mountpoint, output_directory):

    mit = normalized_recursive_directory_iterator(mountpoint)
    oit = normalized_recursive_directory_iterator(origin_mountpoint)

    def emit_removal(o):
        print('Removal:', o[0])

    def emit_creation(m):
        print('Creation:', m[0])

    def emit_compare(m, o):
        if m[2] != o[2] or m[3] != o[3] or m[4] != o[4]:
            print('Metadata change:', o[0])
        elif m[5] != o[5] :
            print('Size change:', o[0])
        elif stat.S_ISREG(m[2]) and filehash(m[1]) != filehash(o[1]):
            print('Content change:', o[0])
        else: # no change
            pass # print('Compare:', m[0])

    m = next(mit, None)
    o = next(oit, None)
    while True:
        if m is None and o is None:
            break
        elif m is None and o is not None:
            emit_removal(o)
        elif m is not None and o is None:
            emit_creation(m)
        elif m[0] < o[0]:
            emit_creation(m)
            m = next(mit, None)
        elif m[0] > o[0]:
            emit_removal(o)
            o = next(oit, None)
        else:
            emit_compare(m, o)
            m = next(mit, None)
            o = next(oit, None)

    #for root, dirs, files in os.walk(path):
     #  dirs.sort()
      # for dirname in dirs:
        #    print(os.path.join(root, dirname))


def command_export(args):
    name, _ = zfs_find(args.reference, focker_type='image')
    mountpoint = zfs_mountpoint(name)
    origin = zfs_parse_output(['zfs', 'get', '-H', 'origin', name])
    origin = origin[2].split('@')[0]
    origin_mountpoint = zfs_mountpoint(origin)
    Q = [ zfs_mountpoint(name) ]
    while len(Q) > 0:
        el = Q.pop()
