#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from ...misc import load_overrides


class CommandConfig:
    def __init__(self):
        self.overrides = load_overrides('command.conf', env_prefix='FOCKER_CMD_', env_hier=True)
