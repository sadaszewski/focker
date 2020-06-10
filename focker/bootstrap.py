import subprocess
import hashlib
from .misc import find_prefix, \
    random_sha256_hexdigest
from .zfs import zfs_poolname, \
    zfs_mountpoint, \
    zfs_tag, \
    zfs_untag, \
    zfs_exists_snapshot_sha256


def command_bootstrap(args):
    if args.no_image + args.empty + args.non_interactive > 1:
        raise ValueError('--no-image, --empty and --non-interactive are mutually exclusive')

    if args.no_image and args.unfinalized:
        raise ValueError('--no-image and --unfinalized are mutually exclusive')

    if args.create_interface:
        create_interface(args)

    if args.no_image:
        print('Image creation disabled')
    elif args.empty:
        bootstrap_empty(args)
    elif args.non_interactive:
        bootstrap_non_interactive(args)
    else:
        bootstrap_interactive(args)


def bootstrap_empty(args):
    sha256 = random_sha256_hexdigest()
    if zfs_exists_snapshot_sha256(sha256):
        raise ValueError('Whew, a SHA256 clash ...')

    poolname = zfs_poolname()
    name = find_prefix(poolname + '/focker/images/', sha256)
    subprocess.check_output(['zfs', 'create', '-o', 'focker:sha256=' + sha256, name])
    zfs_untag(args.tags, focker_type='image')
    zfs_tag(name, args.tags)

    if not args.unfinalized:
        _bootstrap_common_finalize(name)


def _bootstrap_common(args):
    version = subprocess.check_output(['freebsd-version']).decode('utf-8')
    print('FreeBSD version:', version)
    tags = args.tags or [ 'freebsd-' + version.split('-')[0], 'freebsd-latest' ]

    sha256 = hashlib.sha256(('FreeBSD ' + version).encode('utf-8')).hexdigest()
    if zfs_exists_snapshot_sha256(sha256):
        raise ValueError('Image already exists')

    poolname = zfs_poolname()
    name = find_prefix(poolname + '/focker/images/', sha256)
    subprocess.check_output(['zfs', 'create', '-o', 'focker:sha256=' + sha256, name])
    zfs_untag(tags, focker_type='image')
    zfs_tag(name, tags)

    return name


def _bootstrap_common_finalize(name):
    subprocess.check_output(['zfs', 'set', 'rdonly=on', name])
    subprocess.check_output(['zfs', 'snapshot', name + '@1'])


def bootstrap_interactive(args):
    name = _bootstrap_common(args)

    res = subprocess.run(['bsdinstall', 'jail', zfs_mountpoint(name)])
    if res.returncode != 0:
        zfs_run(['zfs', 'destroy', '-r', '-f', name])
        raise ValueError('bsdinstall failed')

    if not args.unfinalized:
        _bootstrap_common_finalize(name)


def bootstrap_non_interactive(args):
    name = _bootstrap_common(args)

    res = subprocess.run(['focker-bsdinstall', zfs_mountpoint(name)])
    if res.returncode != 0:
        zfs_run(['zfs', 'destroy', '-r', '-f', name])
        raise ValueError('focker-bsdinstall failed')

    if not args.unfinalized:
        _bootstrap_common_finalize(name)


def create_interface(args):
    print('Creating interface', args.interface, '...')
    subprocess.check_output(['sysrc', 'cloned_interfaces+=' + args.interface])
    if args.rename_interface:
        print('Renaming interface', args.interface, '->', args.rename_interface)
        subprocess.check_output(['sysrc', 'ifconfig_%s_name=%s' % \
            (args.interface, args.rename_interface)])
    else:
        subprocess.check_output(['sysrc', 'ifconfig_%s_name=%s' % \
            (args.interface, args.interface)])
    subprocess.check_output(['service', 'netif', 'cloneup'])
    print('Interface ready')
