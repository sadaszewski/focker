from ..plugin import Plugin
from tabulate import tabulate
from ..core.zfs import zfs_init


class BootstrapPlugin(Plugin):
    @staticmethod
    def provide_parsers():
        return dict(
            bootstrap=dict(
                aliases=['boot', 'bs', 'b'],
                subparsers=dict(
                    filesystem=dict(
                        aliases=['fs'],
                        func=cmd_bootstrap_filesystem
                    ),
                    interface=dict(
                        aliases=['iface', 'if'],
                        func=cmd_bootstrap_interface,
                        interface=dict(
                            aliases=['i'],
                            type=str,
                            default='lo1'
                        ),
                        rename_interface=dict(
                            aliases=['r'],
                            type=str
                        )
                    ),
                    pfrule=dict(
                        aliases=['pf'],
                        func=cmd_add_pfrule,
                        external_interface=dict(
                            aliases=['eif'],
                            type=str
                        ),
                        jail_interface=dict(
                            aliases=['jif'],
                            type=str,
                            default='lo1'
                        )
                    )
                )
            )
        )


def cmd_bootstrap_filesystem(args):
    print('Creating necessary filesystem objects...')
    zfs_init()
    print('Done.')


def cmd_bootstrap_interface(args):
    print('Creating interface', args.interface, '...')
    focker_subprocess_check_output(['sysrc', 'cloned_interfaces+=' + args.interface])
    if args.rename_interface:
        print('Renaming interface', args.interface, '->', args.rename_interface)
        focker_subprocess_check_output(['sysrc', 'ifconfig_%s_name=%s' % \
            (args.interface, args.rename_interface)])
    else:
        focker_subprocess_check_output(['sysrc', 'ifconfig_%s_name=%s' % \
            (args.interface, args.interface)])
    focker_subprocess_check_output(['service', 'netif', 'cloneup'])
    print('Interface ready')


def cmd_add_pfrule(args):
    if args.external_interface is None:
        iface = focker_subprocess_check_output([ 'ifconfig', '-l' ])
        iface = iface.decode('utf-8').split(' ')
        iface = [ i for i in iface if not i.startswith('lo') ]
        iface = iface[0]
    else:
        iface = args.external_interface
    jail_iface = args.jail_interface
    rule = f'nat on {iface} from ({jail_iface}:network) -> ({iface})'
    with open('/etc/pf.conf', 'a') as f:
        f.write('\n')
        f.write('##### Rule added by Focker #####')
        f.write('\n')
        f.write(rule)
        f.write('\n')
