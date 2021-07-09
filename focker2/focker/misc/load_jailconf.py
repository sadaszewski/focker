from .backup_file import backup_file
import os
import jailconf


def load_jailconf(fname):
    if os.path.exists(fname):
        conf = jailconf.load(fname)
    else:
        conf = jailconf.JailConf()
    return conf


def save_jailconf(conf, fname):
    backup_file(fname)
    conf.write(fname)
