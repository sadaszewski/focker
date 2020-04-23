import subprocess

def jail_run(path, command):
    command = ['jail', '-c', 'interface=lo1', 'ip4.addr=127.0.1.0', 'path=' + path, 'command', '/bin/sh', '-c', command]
    print('Running:', ' '.join(command))
    subprocess.check_output(command)
