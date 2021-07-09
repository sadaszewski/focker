from .process import focker_subprocess_check_output, \
    focker_subprocess_run
from .jailspec import JailSpec
from .osjailspec import OSJailSpec


class PrePostCommandManager:
    def __init__(self, pre_command, post_command):
        self.pre_command = pre_command
        self.post_command = post_command

    def __enter__(self):
        focker_subprocess_check_output(self.pre_command)

    def __exit__(self, exc_type, exc_val, exc_tb):
        focker_subprocess_check_output(self.post_command)


def default_jail_run(im, command):
    spec = JailSpec.from_dict({
        'image': im
    })
    ospec = OSJailSpec.from_jailspec(spec)
    ospec.add()
    focker_subprocess_check_output(['jail', '-c', ospec.name])
    try:
        focker_subprocess_check_output(['jexec', ospec.name, command])
    finally:
        focker_subprocess_check_output(['jail', '-r', ospec.name])
        ospec.remove()
