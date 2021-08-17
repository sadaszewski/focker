import subprocess
import hashlib
from .misc import find_prefix, \
    random_sha256_hexdigest, \
    focker_subprocess_check_output, \
    focker_subprocess_run
from .zfs import zfs_poolname, \
    zfs_mountpoint, \
    zfs_tag, \
    zfs_untag, \
    zfs_exists_snapshot_sha256, \
    zfs_run


def command_bootstrap(args):
    if args.no_image + args.empty + args.non_interactive > 1:
        raise ValueError('--no-image, --empty and --non-interactive are mutually exclusive')

    if args.no_image and args.unfinalized:
        raise ValueError('--no-image and --unfinalized are mutually exclusive')

    if args.create_interface or args.full_auto:
        create_interface(args)

    if args.add_pf_rule or args.full_auto:
        add_pf_rule(args)

    if args.no_image:
        print('Image creation disabled')
    elif args.empty:
        print('Creation of empty image selected')
        bootstrap_empty(args)
    elif args.non_interactive or args.full_auto:
        print('Non-interactive setup selected')
        bootstrap_non_interactive(args)
    else:
        print('Interactive setup selected')
        bootstrap_interactive(args)


def bootstrap_empty(args):
    sha256 = random_sha256_hexdigest()
    if zfs_exists_snapshot_sha256(sha256):
        raise ValueError('Whew, a SHA256 clash ...')

    poolname = zfs_poolname()
    name = find_prefix(poolname + '/focker/images/', sha256)
    focker_subprocess_check_output(['zfs', 'create', '-o', 'focker:sha256=' + sha256, name])
    zfs_untag(args.tags, focker_type='image')
    zfs_tag(name, args.tags)

    if not args.unfinalized:
        _bootstrap_common_finalize(name)


def _bootstrap_common(args):
    version = focker_subprocess_check_output(['freebsd-version']).decode('utf-8')
    print('FreeBSD version:', version)
    tags = args.tags or [ 'freebsd-' + version.split('-')[0], 'freebsd-latest' ]

    sha256 = hashlib.sha256(('FreeBSD ' + version).encode('utf-8')).hexdigest()
    if zfs_exists_snapshot_sha256(sha256):
        raise ValueError('Image already exists')

    poolname = zfs_poolname()
    name = find_prefix(poolname + '/focker/images/', sha256)
    focker_subprocess_check_output(['zfs', 'create', '-o', 'focker:sha256=' + sha256, name])
    zfs_untag(tags, focker_type='image')
    zfs_tag(name, tags)

    return name


def _bootstrap_common_finalize(name):
    focker_subprocess_check_output(['zfs', 'set', 'rdonly=on', name])
    focker_subprocess_check_output(['zfs', 'snapshot', name + '@1'])


def bootstrap_interactive(args):
    name = _bootstrap_common(args)

    res = focker_subprocess_run(['bsdinstall', 'jail', zfs_mountpoint(name)])
    if res.returncode != 0:
        zfs_run(['zfs', 'destroy', '-r', '-f', name])
        raise ValueError('bsdinstall failed')

    if not args.unfinalized:
        _bootstrap_common_finalize(name)


def bootstrap_non_interactive(args):
    name = _bootstrap_common(args)

    res = focker_subprocess_run(['focker-bsdinstall', zfs_mountpoint(name)])
    if res.returncode != 0:
        zfs_run(['zfs', 'destroy', '-r', '-f', name])
        raise ValueError('focker-bsdinstall failed')

    if not args.unfinalized:
        _bootstrap_common_finalize(name)


def create_interface(args):
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


def add_pf_rule(args):
    if args.external_interface is None:
        iface = focker_subprocess_check_output([ 'ifconfig', '-l' ])
        iface = iface.decode('utf-8').split(' ')
        iface = [ i for i in iface if not i.startswith('lo') ]
        iface = iface[0]
    else:
        iface = args.external_interface
    jail_iface = args.rename_interface or args.interface
    rule = f'nat on {iface} from ({jail_iface}:network) -> ({iface})'
    with open('/etc/pf.conf', 'a') as f:
        f.write('\n')
        f.write('##### Rule added by Focker #####')
        f.write('\n')
        f.write(rule)
        f.write('\n')
