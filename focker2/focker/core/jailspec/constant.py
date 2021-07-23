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


def _load_default_jail_param_overrides():
    global DEFAULT_PARAMS
    ovr = load_overrides('jail-defaults.conf')
    DEFAULT_PARAMS = merge_dicts(DEFAULT_PARAMS, ovr)

_load_default_jail_param_overrides()


def _load_jail_name_prefix_override():
    global JAIL_NAME_PREFIX
    ovr = load_overrides('focker.conf', [ 'jail_name_prefix' ])
    JAIL_NAME_PREFIX = ovr.get('jail_name_prefix', JAIL_NAME_PREFIX)

_load_jail_name_prefix_override()
