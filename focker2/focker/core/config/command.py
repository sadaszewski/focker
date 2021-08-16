from ...misc import load_overrides


class CommandConfig:
    def __init__(self):
        self.overrides = load_overrides('command.conf', env_prefix='FOCKER_CMD_', env_hier=True)
