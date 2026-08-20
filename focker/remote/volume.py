from .client import setup_client
import shlex
import sys
import json
from paramiko import SSHClient
from pathlib import Path
import os
import datetime
import gzip
from concurrent.futures import ThreadPoolExecutor


def zfs_parse_output(client: SSHClient, command: list[str]):
    command = list(command)
    if "--json" not in command:
        command.append("--json")
    _, stdout, stderr = client.exec_command(shlex.join(command))
    stdout = stdout.read().decode()
    stderr = stderr.read().decode()
    if stderr:
        sys.stderr.write(stderr)
    return json.loads(stdout)


def cmd_remote_volume_backup(args):
    client = setup_client()    
    res = zfs_parse_output(client, ["zfs", "list", "-t", "filesystem", "-o", "focker:tags,mountpoint"])
    res = [
        ds for ds in res['datasets'].values()
            if args.remote_tag in ds.get('properties', {}).get('focker:tags', {}).get('value', '').split(' ') and
                ds['name'].split('/')[-2] == 'volumes'
    ]
    if len(res) == 0:
        raise KeyError("Specified volume not found")
    if len(res) > 1:
        raise KeyError("Ambiguous volume tag")
    res = res[0]
    host = os.environ["FOCKER_REMOTE_HOST"]
    path = Path.home() / ".focker" / "remote" / "volume" / "backup" / host
    path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    path = path / (args.remote_tag + "_" + timestamp + ".tar.gz")
    mountpoint = res['properties']['mountpoint']['value']
    print(f"{path=}, {mountpoint=}")
    with gzip.open(path, "wb") as f:
        stdin, stdout, stderr = client.exec_command(shlex.join([
            "tar",
            "-C", mountpoint,
            "--numeric-owner",
            "-c",
            ".",
        ]))
        stdin.close()
        def read_stdout(stdout):
            while True:
                data = stdout.read(4 * 1024 * 1024)
                if not data:
                    break
                f.write(data)
        with ThreadPoolExecutor(max_workers=2) as ex:
            stderr = ex.submit(stderr.read)
            stdout = ex.submit(read_stdout, stdout)
        stderr = stderr.result()
        stdout = stdout.result()
        if stderr:
            print(stderr)


def cmd_remote_volume_restore(args):
    raise NotImplementedError


PARSERS = {
    "remote-volume": dict(
        aliases=["rem-vol", "rv"],
        subparsers=dict(
            backup=dict(
                func=cmd_remote_volume_backup,
                remote_tag=dict(
                    positional=True,
                    type=str,
                ),
                local_backup_file=dict(
                    aliases=["f"],
                    required=False,
                    type=str,
                ),
            ),
            restore=dict(
                func=cmd_remote_volume_restore,
                remote_tag=dict(
                    positional=True,
                    type=str,
                ),
                local_backup_file=dict(
                    aliases=["f"],
                    required=False,
                    type=str,
                ),
            ),
        ),
    )
}
