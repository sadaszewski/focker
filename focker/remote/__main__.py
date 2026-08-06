from argparse import ArgumentParser
import os
from paramiko import SSHConfig, PKey, SSHClient, WarningPolicy
from pathlib import Path
import getpass
import sys
import shlex
import logging
from ..materialize_parsers import materialize_parsers
from . import image, volume, compose
from ..misc import merge_dicts
from functools import reduce


PARSER_DEFS = reduce(merge_dicts, [
    image.PARSERS,
    volume.PARSERS,
    compose.PARSERS,
])


def create_parser():
    parser = ArgumentParser(allow_abbrev=False)
    subp = parser.add_subparsers()

    materialize_parsers(PARSER_DEFS, subp, {})

    return parser


def setup_logging():
    if "FOCKER_REMOTE_LOG_LEVEL" in os.environ:
        log_level = os.environ["FOCKER_REMOTE_LOG_LEVEL"]
        if log_level.upper() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            log_level = getattr(logging, log_level.upper())
            logging.basicConfig(level=log_level)
    logger = logging.getLogger("focker.remote")
    return logger


def setup_client():
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
    return client


def forward_command():
    client = setup_client()
    logger = logging.getLogger("focker.remote")
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


def main():
    parser = create_parser()

    for k, v in PARSER_DEFS.items():
        if sys.argv[1] == k or sys.argv[1] in v.get("aliases", []):
            args = parser.parse_args()
            args.func(args)
            return

    if "-h" in sys.argv[1:] or "--help" in sys.argv[1]:
        parser.print_help()
        forward_command()
        return
    
    forward_command()


if __name__ == "__main__":
    main()
