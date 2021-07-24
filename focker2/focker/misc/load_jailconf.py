from .backup_file import backup_file
import os
from ..jailconf import load, \
    dump, \
    JailConf


def load_jailconf(fname='/etc/jail.conf'):
    if os.path.exists(fname):
        conf = load(fname)
    else:
        conf = JailConf()
    return conf


def save_jailconf(conf, fname='/etc/jail.conf'):
    backup_file(fname)
    dump(conf, fname)
