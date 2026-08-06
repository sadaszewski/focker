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
                local_focker_dir=dict(
                    positional=True,
                    type=str,
                ),
            ),
            backup=dict(
                func=cmd_remote_compose_backup,
                remote_reference=dict(
                    positional=True,
                    type=str,
                ),
                local_backup_file=dict(
                    required=False,
                    type=str,
                ),
            ),
            restore=dict(
                func=cmd_remote_compose_restore,
                remote_reference=dict(
                    positional=True,
                    type=str,
                ),
                local_backup_file=dict(
                    required=False,
                    type=str,
                ),
            ),
        ),
    )
}
