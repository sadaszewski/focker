from .misc import random_sha256_hexdigest
from .zfs import *


def command_volume_create(args):
    sha256 = random_sha256_hexdigest()
    poolname = zfs_poolname()
    for pre in range(7, 64):
        name = poolname + '/focker/volumes/' + sha256[:pre]
        if not zfs_exists(name):
            break
    zfs_run(['zfs', 'create', '-o', 'focker:sha256=' + sha256, name])
    zfs_tag(name, args.tags)


def command_volume_prune(args):
    raise NotImplementedError


def command_volume_list(args):
    raise NotImplementedError


def command_volume_tag(args):
    raise NotImplementedError


def command_volume_untag(args):
    raise NotImplementedError
