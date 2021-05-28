from .zfs import zfs_list, \
    zfs_run, \
    zfs_poolname
from .misc import find_prefix
from typing import Tuple, \
    Dict


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


def zfs_shortest_unique_name(name: str, focker_type: str) -> str:
    poolname = zfs_poolname()
    head = f'{poolname}/{focker_type}s/'
    return find_prefix(head, name)


def zfs_snapshot(snapshot_name: str) -> None:
    zfs_run([ 'zfs', 'snapshot', snapshot_name ])


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
