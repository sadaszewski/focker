from .process import focker_subprocess_check_output
from typing import Union


class Mount:
    def __init__(self, source: Union[str, object],
        mountpoint: Union[str, object],
        fs_type: str = 'nullfs') -> None:

        self.source = source if isinstance(source, str) else source.path
        self.mountpoint = mountpoint if isinstance(mountpoint, str) else mountpoint.path
        self.fs_type = fs_type

    def mount(self) -> None:
        focker_subprocess_check_output(['mount', '-t', self.fs_type, self.source, self.mountpoint])

    def umount(self) -> None:
        focker_subprocess_check_output(['umount', self.mountpoint])


class MountManager:
    def __init__(self, mounts):
        self.mounts = mounts

    def __enter__(self):
        for m in self.mounts:
            m.mount()

    def __exit__(self, exc_type, exc_val, exc_tb):
        for m in self.mounts:
            m.umount()
