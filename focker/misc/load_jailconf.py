#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


import os
import json


def jailconf_dir():
    from ..core.config import FOCKER_CONFIG
    return os.path.join(FOCKER_CONFIG.zfs.root_mountpoint, 'jailconf')


def _parse_str_values(d):
    def _inner(v):
        if v.__class__ == str and v.isnumeric():
            v = int(v)
        elif v == 'true':
            v = True
        elif v == 'false':
            v = False
        return v

    if isinstance(d, dict):
        return { k: _parse_str_values(v) for k, v in d.items() }
    elif isinstance(d, list):
        return [ _inner(v) for v in d ]
    else:
        return _inner(d)


def _json_load(f):
    return _parse_str_values(json.load(f))


def _json_dump(entry, f):
    json.dump(_parse_str_values(entry), f)


def load_jailconf():
    conf = {}
    dnam = jailconf_dir()
    for fnam in os.listdir(dnam):
        if not fnam.endswith('.json'):
            continue
        with open(os.path.join(dnam, fnam)) as f:
            entry = _json_load(f)
        name, _ = os.path.splitext(fnam)
        conf[name] = entry
    return conf


def jailconf_load_jail(*, name):
    fnam = os.path.join(jailconf_dir(), f'{name}.json')
    with open(fnam) as f:
        return _json_load(f)


def jailconf_jail_exists(*, name):
    fnam = os.path.join(jailconf_dir(), f'{name}.json')
    return os.path.exists(fnam)


def jailconf_add_jail(*, name, entry):
    fnam = os.path.join(jailconf_dir(), f'{name}.json')
    with open(fnam + '.tmp', 'w') as f:
        _json_dump(entry, f)
    os.rename(fnam + '.tmp', fnam)


def jailconf_remove_jail(*, name):
    fnam = os.path.join(jailconf_dir(), f'{name}.json')
    os.unlink(fnam)
