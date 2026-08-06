def cmd_remote_compose_build(args):
    raise NotImplementedError


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
