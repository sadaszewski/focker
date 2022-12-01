#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from .process import focker_subprocess_check_output
from typing import Union
import os


class Mount:
    def __init__(self, source: Union[str, object],
        mountpoint: Union[str, object],
        fs_type: str = 'nullfs') -> None:

        self.source = source if isinstance(source, str) else source.path
        self.mountpoint = mountpoint if isinstance(mountpoint, str) else mountpoint.path
        self.fs_type = fs_type


class MountSpec:
    def __init__(self, source_spec, mountpoint_spec):
        self.source_spec = source_spec
        self.mountpoint_spec = mountpoint_spec


def mount_from_spec(spec: MountSpec, path: str) -> Mount:
    mountpoint = os.path.join(path, spec.mountpoint_spec.strip('/'))

    if spec.source_spec.startswith('/'):
        return Mount(spec.source_spec, mountpoint)

    vol, *vol_path = spec.source_spec.split('/')
    from .volume import Volume
    vol = Volume.from_any_id(vol, strict=True)
    source = os.path.join(vol.path, *vol_path)

    return Mount(source, mountpoint)
