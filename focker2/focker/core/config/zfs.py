#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from ...misc import load_overrides
from ..zfs import zfs_poolname


class ZfsConfig:
    def __init__(self):
        conf = load_overrides('focker.conf', env_prefix='FOCKER_CONF_')
        self.root_dataset = conf['root_dataset'] if 'root_dataset' in conf \
            else zfs_poolname() + '/focker'
        self.root_mountpoint = conf['root_mountpoint'] if 'root_mountpoint' in conf \
            else '/focker'
