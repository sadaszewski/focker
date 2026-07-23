from argparse import ArgumentParser
import os
from paramiko import SSHConfig, PKey, SSHClient, WarningPolicy
from pathlib import Path
import getpass


def create_parser():
    parser = ArgumentParser()


def main():
    if "FOCKER_REMOTE_HOST" not in os.environ:
        raise KeyError("FOCKER_REMOTE_HOST environment variable must be set")
    remote_host = os.environ["FOCKER_REMOTE_HOST"]
    ssh_config_path = Path.home() / ".ssh" / "config"
    print(f"{remote_host=}")

    hostname = None
    port = None
    username = None
    identityfile = None

    hostname = remote_host
    if "@" in hostname:
        username, hostname = hostname.split("@")[:2]
    if ":" in remote_host:
        hostname, port = hostname.split(":")[:2]
    print(f"{hostname=}")
    if ssh_config_path.exists():
        config = SSHConfig.from_path(ssh_config_path)
        if hostname in config.get_hostnames():
            lookup = config.lookup(hostname)
            print(f"{lookup=}")
            if "port" in lookup and port is None: port = lookup["port"]
            if "user" in lookup and username is None: username = lookup["user"]
            if "identityfile" in lookup and identityfile is None: identityfile = lookup["identityfile"][0]
            if "hostname" in lookup: hostname = lookup["hostname"]
    
    port = port or "22"
    username = username or getpass.getuser()

    if identityfile is not None:
        pkey = PKey.from_path(identityfile, password=os.environ.get("FOCKER_IDENTITY_FILE_PASSPHRASE").encode())
        print("Loaded pkey")
        password = None
    else:
        password = getpass.getpass()
        pkey = None

    print(f"{hostname=}, {port=}, {username=}, {identityfile=}")
    
    client = SSHClient()
    client.set_missing_host_key_policy(WarningPolicy())
    client.connect(username=username, hostname=hostname, port=int(port), pkey=pkey, password=password)
    print("SSH connected!")


if __name__ == "__main__":
    main()
