#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#

from ..core.zfs import zfs_list
import os
import json


def load_jailconf(*, jail_name=None, return_jfs_list=False):
    lst = zfs_list(['name', 'mountpoint'], focker_type='jail')
    conf = {}
    for name, mountpoint, *_ in lst:
        tmp = os.path.join(mountpoint, '.ssman', 'jail_config.json')
        if not os.path.exists(tmp):
            continue
        with open(tmp) as f:
            tmp = json.load(f)
            conf[tmp['name']] = tmp
    if jail_name:
        conf = conf[jail_name]
    res = conf
    if return_jfs_list:
        res = (res,) + (lst,)
    return res


def save_jailconf(conf, *, jail_name):
    conf = dict(conf)
    conf['name'] = jail_name
    with open(os.path.join(conf['path'], '.ssman', 'jail_config.json'), 'w') as f:
        json.dump(self.params, f)
