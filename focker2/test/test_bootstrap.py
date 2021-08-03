from focker.__main__ import main
import os

"""

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

"""

def _read_file_if_exists(fname, default=None):
    if os.path.exists(fname):
        with open(fname, 'r') as f:
            return f.read()

    return default

class TestBootstrap:
    def test01_pfrule(self):
        old = _read_file_if_exists('/etc/pf.conf', '')
        try:
            cmd = [ 'bootstrap', 'pfrule' ]
            main(cmd)
            with open('/etc/pf.conf', 'r') as f:
                new = f.read()
            assert new[len(old):].startswith('\n##### Rule added by Focker #####\n')
        finally:
            with open('/etc/pf.conf', 'w') as f:
                f.write(old)

    def test02_iface(self):
        cmd = [ 'bootstrap', 'iface' ]
        old = _read_file_if_exists('/etc/rc.conf', '')
        try:
            main(cmd)
            new = _read_file_if_exists('/etc/rc.conf', '')
            new = new.split('\n')
            new = [ ln for ln in new if ln.startswith('cloned_interfaces=') and 'tun0' in ln ]
            assert len(new) == 1
        finally:
            with open('/etc/rc.conf', 'w') as f:
                f.write(old)
