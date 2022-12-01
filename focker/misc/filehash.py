#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


import hashlib
from contextlib import ExitStack


def filehash(fname_or_fp):
    h = hashlib.sha256()
    with ExitStack() as stack:
        if isinstance(fname_or_fp, str):
            f = open(fname_or_fp, 'rb')
            stack.callback(f.close)
        else:
            f = fname_or_fp
        while True:
            data = f.read(1024*1024*4)
            if not data:
                break
            h.update(data)
    res = h.hexdigest()
    return res
