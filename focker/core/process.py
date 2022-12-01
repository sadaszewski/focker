#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


import subprocess
from subprocess import CalledProcessError


def focker_subprocess_run(command, *args, check=True, **kwargs):
    return subprocess.run(command, check=check, *args, **kwargs)


def focker_subprocess_check_output(command, *args, **kwargs):
    return subprocess.check_output(command, *args, **kwargs)
