#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from ...core.process import focker_subprocess_check_output


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
