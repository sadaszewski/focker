from paramiko import SSHClient, ChannelFile
import shlex
from concurrent.futures import ThreadPoolExecutor
import sys
import logging
import shutil


def read_outputs(stdout: ChannelFile, stderr: ChannelFile, stdin: ChannelFile, stdin_fp=None):
    exit_status = stdout.channel
    with ThreadPoolExecutor(max_workers=3) as ex:
        if stdin_fp is None:
            stdin.close()
        else:
            stdin_fut = ex.submit(shutil.copyfileobj, stdin_fp, stdin)
        stdout = ex.submit(stdout.read)
        stderr = ex.submit(stderr.read)
        if stdin_fp is not None:
            _ = stdin_fut.result()
        stdin.close()
    stdout = stdout.result()
    stderr = stderr.result()
    exit_status = exit_status.recv_exit_status()
    return stdout, stderr, exit_status


def check_output(client: SSHClient, command: list[str], stdin_fp=None):
    stdin, stdout, stderr = client.exec_command(shlex.join(command))
    stdout, stderr, exit_status = read_outputs(stdout, stderr, stdin, stdin_fp)
    if stderr:
        sys.stderr.write(stderr.decode())
    if exit_status != 0:
        raise RuntimeError(f"Command returned exit status: {exit_status}")
    return stdout


def unpack_tar_gz(client: SSHClient, dest: str, archive_fp):
    check_output(
        client,
        ["tar", "-C", dest, "-zx"],
        archive_fp,
    )


class TemporaryDirectory:
    def __init__(self, client: SSHClient):
        self.client = client
        self.dirname = None
        self.logger = logging.getLogger("focker.remote.misc.TemporaryDirectory")

    def __enter__(self):
        self.dirname = check_output(self.client, ["mktemp", "-d"]).decode().strip()
        self.logger.debug(f"{self.dirname=}")
        return self.dirname

    def __exit__(self, *_args):
        check_output(self.client, ["rmdir", self.dirname])
        self.logger.debug(f"{self.dirname=} removed")


def main():
    import logging
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("focker.remote").setLevel(logging.DEBUG)
    from focker.remote.client import setup_client
    client = setup_client()
    with TemporaryDirectory(client) as d, \
        open("/home/sadaszew/.focker/remote/volume/backup/explorer_root/test-volume_20260820174216.tar.gz", "rb") as f:
        unpack_tar_gz(client, d, f)
        check_output(client, ["rm", "-v", f"{d}/hello.txt"])


if __name__ == "__main__":
    main()
