def cmd_remote_image_build(args):
    raise NotImplementedError


def cmd_remote_image_backup(args):
    raise NotImplementedError


def cmd_remote_image_restore(args):
    raise NotImplementedError


PARSERS = {
    "remote-image": dict(
        aliases=["rem-im", "ri"],
        subparsers=dict(
            build=dict(
                func=cmd_remote_image_build,
                local_focker_dir=dict(
                    positional=True,
                    type=str,
                ),
            ),
            backup=dict(
                func=cmd_remote_image_backup,
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
                func=cmd_remote_image_restore,
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
