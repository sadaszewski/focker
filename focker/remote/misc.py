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


def forward_outputs(
    stdout: ChannelFile, stderr: ChannelFile, stdin: ChannelFile, *,
    stdin_fp=None, stdout_fp=None, stderr_fp=None,
):
    if stdout_fp is None:
        stdout_fp = sys.stdout.buffer
    if stderr_fp is None:
        stderr_fp = sys.stderr.buffer
    exit_status = stdout.channel
    with ThreadPoolExecutor(max_workers=3) as ex:
        if stdin_fp is None:
            stdin.close()
        else:
            stdin_fut = ex.submit(shutil.copyfileobj, stdin_fp, stdin)
        stdout = ex.submit(shutil.copyfileobj, stdout, stdout_fp)
        stderr = ex.submit(shutil.copyfileobj, stderr, stderr_fp)
        if stdin_fp is not None:
            _ = stdin_fut.result()
        stdin.close()
    exit_status = exit_status.recv_exit_status()
    return exit_status


def check_output(client: SSHClient, command: list[str], stdin_fp=None):
    stdin, stdout, stderr = client.exec_command(shlex.join(command))
    stdout, stderr, exit_status = read_outputs(stdout, stderr, stdin, stdin_fp)
    if stderr:
        sys.stderr.write(stderr.decode())
    if exit_status != 0:
        raise RuntimeError(f"Command returned exit status: {exit_status}")
    return stdout


def run(client: SSHClient, command: list[str], *, stdin_fp=None, stdout_fp=None, stderr_fp=None, raise_for_exit_status=True):
    stdin, stdout, stderr = client.exec_command(shlex.join(command))
    exit_status = forward_outputs(
        stdout, stderr, stdin,
        stdin_fp=stdin_fp, stdout_fp=stdout_fp, stderr_fp=stderr_fp
    )
    if exit_status != 0 and raise_for_exit_status:
        raise RuntimeError(f"Command returned exit status: {exit_status}")


def unpack_tar_gz(client: SSHClient, dest: str, archive_fp):
    check_output(
        client,
        ["tar", "-C", dest, "-zx"],
        archive_fp,
    )


class UnpackTarGz:
    def __init__(self, client: SSHClient, dest: str, *, safe_prefixes=[]):
        self.client = client
        self.dest = dest
        self.safe_prefixes = safe_prefixes

    def unpack(self, archive_fp):
        unpack_tar_gz(self.client, self.dest, archive_fp)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        safe_delete(self.client, self.dest, self.safe_prefixes)


def safe_delete(client: SSHClient, dirname: str, safe_prefixes=[]):
    logger = logging.getLogger("focker.remote")
    res: bytes = check_output(
        client,
        ["find", dirname, "-mindepth", "1", "-print"]
    )
    res = res.decode().splitlines()
    logger.debug(f"{res=}")
    if dirname == "/" or not all(any(p.startswith(x) for x in safe_prefixes) for p in res):
        raise RuntimeError("Unsafe delete attempted")
    check_output(
        client,
        ["find", dirname, "-mindepth", "1", "-delete"]
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
