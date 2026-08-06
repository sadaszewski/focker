def cmd_remote_volume_backup(args):
    raise NotImplementedError


def cmd_remote_volume_restore(args):
    raise NotImplementedError


PARSERS = {
    "remote-volume": dict(
        aliases=["rem-vol", "rv"],
        subparsers=dict(
            backup=dict(
                func=cmd_remote_volume_backup,
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
                func=cmd_remote_volume_restore,
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
