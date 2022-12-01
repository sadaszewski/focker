#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


import os
from .. import yaml


def load_overrides(fname, env_prefix='FOCKER_', env_hier=False):
    res = None
    for p in [ os.path.expanduser('~/.focker'), '/usr/local/etc/focker',
        '/etc/focker' ]:
        p = os.path.join(p, fname)
        if not os.path.exists(p):
            continue
        with open(p) as f:
            res = yaml.safe_load(f)
        break
    if res is None:
        res = {}
    for k, v in os.environ.items():
        if not k.startswith(env_prefix):
            continue
        k = k[len(env_prefix):].lower()
        if env_hier:
            k = k.split('_')
            r = res
            for p in k[:-1]:
                if not p in r:
                    r[p] = {}
                r = r[p]
                if not isinstance(r, dict):
                    raise TypeError(f'Expected dictionary, found {r.__class__.__name__} while traversing keys {k}')
            r[k[-1]] = v
        else:
            res[k] = v
    return res
