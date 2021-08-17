#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from ...misc import merge_dicts, \
    load_overrides


DEFAULT_PARAMS = {
    'persist': True,
    'interface': 'lo1',
    'ip4.addr': '127.0.1.0',
    'mount.devfs': True,
    'exec.clean': True,
    'exec.start': '/bin/sh /etc/rc',
    'exec.stop': '/bin/sh /etc/rc.shutdown'
}


JAIL_NAME_PREFIX = 'focker_'


class JailConfig:
    def __init__(self):
        ovr = load_overrides('jail-defaults.conf', env_prefix='FOCKER_JAIL_DEFAULTS_')
        self.default_params = merge_dicts(DEFAULT_PARAMS, ovr)

        ovr = load_overrides('focker.conf', env_prefix='FOCKER_CONF_')
        self.name_prefix = ovr.get('jail_name_prefix', JAIL_NAME_PREFIX)
