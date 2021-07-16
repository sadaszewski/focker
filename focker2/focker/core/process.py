import subprocess


def focker_subprocess_run(command, *args, check=True, **kwargs):
    return subprocess.run(command, check=check, *args, **kwargs)


def focker_subprocess_check_output(command, *args, **kwargs):
    return subprocess.check_output(command, *args, **kwargs)
