from .zfs import zfs_list
from typing import Tuple


def zfs_find_sha256(sha256: str, focker_type: str,
    zfs_type: str) -> Tuple[str, str]:

    lst = zfs_list(fields=['name', 'mountpoint', 'focker:sha256'],
        focker_type=focker_type, zfs_type=zfs_type)
    lst = [ a for a in lst if a[2] == sha256 ]
    if len(lst) == 0:
        return None
    if len(lst) > 1:
        raise RuntimeError('Ambiguous SHA256 - this should never happen')
    return lst[0][:2]
