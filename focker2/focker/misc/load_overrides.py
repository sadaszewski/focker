import os
import ruamel.yaml as yaml


def load_overrides(fname, names=[]):
    res = {}
    for p in [ os.path.expanduser('~/.focker'), '/usr/local/etc/focker',
        '/etc/focker' ]:
        p = os.path.join(p, fname)
        if os.path.exists(p):
            with open(p) as f:
                res = yaml.safe_load(f)
            break
    for nam in names:
        nam_1 = 'FOCKER_' + nam.upper()
        if nam_1 in os.environ:
            res[nam] = os.environ[nam_1]
    return res
