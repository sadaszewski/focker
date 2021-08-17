#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from ...core.process import focker_subprocess_check_output
from ...misc import backup_file


def cmd_bootstrap_pfrule(args):
    if args.external_interface is None:
        iface = focker_subprocess_check_output([ 'ifconfig', '-l' ])
        iface = iface.decode('utf-8').split(' ')
        iface = [ i for i in iface if not i.startswith('lo') ]
        iface = iface[0]
    else: # pragma: no cover
        iface = args.external_interface
    jail_iface = args.jail_interface
    rule = f'nat on {iface} from ({jail_iface}:network) -> ({iface})'
    backup_file('/etc/pf.conf')
    with open('/etc/pf.conf', 'a') as f:
        f.write('\n')
        f.write('##### Rule added by Focker #####')
        f.write('\n')
        f.write(rule)
        f.write('\n')
    print('Rule added to /etc/pf.conf')
