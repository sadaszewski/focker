import logging
from pathlib import Path
import os
from paramiko import SSHConfig, SSHClient, RejectPolicy, PKey, Agent
import getpass
import shlex
import sys


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
    agent = Agent()

    if len(agent.get_keys()) > 0:
        pkey = agent.get_keys()[0]
        logger.debug("Using PKey from agent...")
        password = None
    elif identityfile is not None:
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
    client.load_system_host_keys()
    client.set_missing_host_key_policy(RejectPolicy())
    client.connect(username=username, hostname=hostname, port=int(port), pkey=pkey, password=password)
    logger.debug("SSH connected!")
    return client


def forward_command(client):
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
