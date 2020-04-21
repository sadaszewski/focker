import subprocess

def jail_run(path, command):
    subprocess.check_output(['jail', '-c', 'path=' + path, 'command', '/bin/sh', '-c', command)
