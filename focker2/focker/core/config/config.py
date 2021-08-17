#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from ...misc import load_overrides
from .jail import JailConfig
from .zfs import ZfsConfig
from .command import CommandConfig


class FockerConfig:
    def __init__(self):
        self.jail = JailConfig()
        self.zfs = ZfsConfig()
        self.command = CommandConfig()
