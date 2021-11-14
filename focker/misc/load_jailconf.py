#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from .backup_file import backup_file
import os
from ..jailconf import load, \
    dump, \
    JailConf
from ..core.cache import JailConfCache


def load_jailconf(fname='/etc/jail.conf'):
    if JailConfCache.is_available():
        return JailConfCache.instance()
    elif os.path.exists(fname):
        conf = load(fname)
    else:
        conf = JailConf()
    return conf


def save_jailconf(conf, fname='/etc/jail.conf'):
    backup_file(fname)
    with open(fname, 'w') as f:
        dump(conf, f)
