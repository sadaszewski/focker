from argparse import ArgumentParser
import os
from paramiko import SSHConfig, PKey, SSHClient, WarningPolicy
from pathlib import Path
import getpass
import sys
import shlex
import logging


def main():
    if "FOCKER_REMOTE_LOG_LEVEL" in os.environ:
        log_level = os.environ["FOCKER_REMOTE_LOG_LEVEL"]
        if log_level.upper() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            log_level = getattr(logging, log_level.upper())
            logging.basicConfig(level=log_level)
    logger = logging.getLogger("focker.remote")

    if "FOCKER_REMOTE_HOST" not in os.environ:
        raise KeyError("FOCKER_REMOTE_HOST environment variable must be set")
    remote_host = os.environ["FOCKER_REMOTE_HOST"]
    ssh_config_path = Path.home() / ".ssh" / "config"
    logger.debug(f"{remote_host=}")

    hostname = None
    port = None
    username = None
    identityfile = None

    hostname = remote_host
    if "@" in hostname:
        username, hostname = hostname.split("@")[:2]
    if ":" in remote_host:
        hostname, port = hostname.split(":")[:2]
    logger.debug(f"{hostname=}")
    if ssh_config_path.exists():
        config = SSHConfig.from_path(ssh_config_path)
        if hostname in config.get_hostnames():
            lookup = config.lookup(hostname)
            logger.debug(f"{lookup=}")
            if "port" in lookup and port is None: port = lookup["port"]
            if "user" in lookup and username is None: username = lookup["user"]
            if "identityfile" in lookup and identityfile is None: identityfile = lookup["identityfile"][0]
            if "hostname" in lookup: hostname = lookup["hostname"]
    
    port = port or "22"
    username = username or getpass.getuser()

    if identityfile is not None:
        passphrase = os.environ.get("FOCKER_IDENTITY_FILE_PASSPHRASE").encode() \
            if "FOCKER_IDENTITY_FILE_PASSPHRASE" in os.environ else None
        pkey = PKey.from_path(identityfile, password=passphrase)
        logger.debug("Loaded pkey")
        password = None
    else:
        password = getpass.getpass()
        pkey = None

    logger.debug(f"{hostname=}, {port=}, {username=}, {identityfile=}")
    
    client = SSHClient()
    client.set_missing_host_key_policy(WarningPolicy())
    client.connect(username=username, hostname=hostname, port=int(port), pkey=pkey, password=password)
    logger.debug("SSH connected!")

    width, height = os.get_terminal_size()
    logger.debug(f"{width=}, {height=}")
    # shell = client.invoke_shell(width=width, height=height)
    command = shlex.join(["focker"] + sys.argv[1:])
    logger.debug(f"{command=}")
    stdin, stdout, stderr = client.exec_command(command)
    stdout = stdout.read().decode()
    stderr = stderr.read().decode()
    if stdout:
        sys.stdout.write(stdout)
    if stderr:
        sys.stderr.write(stderr)



if __name__ == "__main__":
    main()
