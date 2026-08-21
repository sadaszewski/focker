from paramiko import SSHClient, ChannelFile
import shlex
from concurrent.futures import ThreadPoolExecutor
import sys
import logging


def read_outputs(stdout: ChannelFile, stderr: ChannelFile):
    with ThreadPoolExecutor(max_workers=2) as ex:
        stdout = ex.submit(stdout.read)
        stderr = ex.submit(stderr.read)
        stdout = stdout.result().decode()
        stderr = stderr.result().decode()
    return stdout, stderr


def check_output(client: SSHClient, command: list[str]):
    stdin, stdout, stderr = client.exec_command(shlex.join(command))
    stdin.close()
    stdout, stderr = read_outputs(stdout, stderr)
    if stderr:
        sys.stderr.write(stderr)
    return stdout


class TemporaryDirectory:
    def __init__(self, client: SSHClient):
        self.client = client
        self.dirname = None
        self.logger = logging.getLogger("focker.remote.misc.TemporaryDirectory")

    def __enter__(self):
        self.dirname = check_output(self.client, ["mktemp", "-d"]).strip()
        self.logger.debug(f"{self.dirname=}")
        return self.dirname

    def __exit__(self, *_args):
        check_output(self.client, ["rmdir", self.dirname])
        self.logger.debug(f"{self.dirname=} removed")
