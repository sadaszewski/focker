#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from ...core import Image, \
    zfs_init


def cmd_bootstrap_filesystem(args):
    print('Creating necessary filesystem objects...')
    zfs_init()
    print('Done.')


def cmd_bootstrap_empty(args):
    im = Image.create()
    im.add_tags(args.tags)
    print('Created', im.name, 'mounted at', im.path, 'with tags:', args.tags)


def cmd_bootstrap_finalize(args):
    im = Image.from_any_id(args.reference)
    im.finalize()
    print('Finalized', im.snapshot_name)
