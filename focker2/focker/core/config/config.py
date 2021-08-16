from ...misc import load_overrides
from .jail import JailConfig
from .zfs import ZfsConfig
from .command import CommandConfig


class FockerConfig:
    def __init__(self):
        self.jail = JailConfig()
        self.zfs = ZfsConfig()
        self.command = CommandConfig()
