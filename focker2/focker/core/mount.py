from .process import focker_subprocess_check_output
from typing import Union


class Mount:
    def __init__(self, source: Union[str, object],
        mountpoint: Union[str, object],
        fs_type: str = 'nullfs') -> None:

        self.source = source if isinstance(source, str) else source.path
        self.mountpoint = mountpoint if isinstance(mountpoint, str) else mountpoint.path
        self.fs_type = fs_type
