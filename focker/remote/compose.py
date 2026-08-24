from .client import setup_client
from pathlib import Path
import tempfile
import subprocess
from . import misc
import logging


def cmd_remote_compose_build(args):
    if args.context_dir is not None:
        context_dir = Path(args.context_dir).resolve()
    else:
        context_dir = Path(args.local_spec_filename).parent.resolve()
    local_spec_filename: Path = Path(args.local_spec_filename).resolve()
    local_spec_filename = local_spec_filename.relative_to(context_dir)
    logger = logging.getLogger("focker.remote")
    logger.debug(f"{context_dir=}, {local_spec_filename=}")
    with tempfile.TemporaryDirectory() as d:
        logger.debug(f"{d=}")
        print("Preparing context...")
        subprocess.run([
            "tar",
            "-C", str(context_dir),
            "-cf",
            str(Path(d) / "context.tar"),
            ".",
        ])
        subprocess.run([
            "gzip",
            str(Path(d) / "context.tar"),
        ])
        context_size = (Path(d) / "context.tar.gz").stat().st_size
        print("Context size: {:.02f} MB ({} bytes)".format(context_size / (1024 * 1024), context_size))
        client = setup_client()
        with misc.TemporaryDirectory(client) as d_remote, \
            (Path(d) / "context.tar.gz").open("rb") as f, \
            misc.UnpackTarGz(client, d_remote, safe_prefixes=[f"{tempfile.gettempdir()}/"]) as u:

            logger.debug(f"{d_remote=}")

            print("Sending context...")
            u.unpack(f)

            cmd = [
                "focker",
                "compose",
                "build",
            ]
            if args.squeeze:
                cmd.append("--squeeze")
            if args.fenv is not None:
                cmd.append("--fenv")
                cmd += args.fenv
            cmd.append((Path(d_remote) / local_spec_filename).as_posix())
            print("Running...")
            misc.run(client, cmd, raise_for_exit_status=False)

            print("Done.")


def cmd_remote_compose_backup(args):
    raise NotImplementedError


def cmd_remote_compose_restore(args):
    raise NotImplementedError


PARSERS = {
    "remote-compose": dict(
        aliases=["rem-comp", "rc"],
        subparsers=dict(
            build=dict(
                func=cmd_remote_compose_build,
                local_spec_filename=dict(
                    positional=True,
                    type=str,
                ),
                context_dir=dict(
                    type=str,
                    required=False,
                ),
                squeeze=dict(
                    action='store_true',
                ),
                fenv=dict(
                    type=str,
                    nargs='+',
                ),
            ),
            backup=dict(
                func=cmd_remote_compose_backup,
                local_spec_filename=dict(
                    positional=True,
                    type=str,
                ),
                local_backup_directory=dict(
                    aliases=["d"],
                    required=False,
                    type=str,
                ),
            ),
            restore=dict(
                func=cmd_remote_compose_restore,
                local_spec_filename=dict(
                    positional=True,
                    type=str,
                ),
                local_backup_directory=dict(
                    aliases=["d"],
                    required=False,
                    type=str,
                ),
            ),
        ),
    )
}
