from ...core import focker_subprocess_run, \
    focker_subprocess_check_output, \
    CalledProcessError, \
    Image
import os
import shutil


def cmd_bootstrap_install(args):
    env = dict(os.environ)
    if args.version:
        version = args.version
        distsite = focker_subprocess_check_output('focker-mirrorselect').strip().decode('utf-8')
        distsite = distsite.split('/')[:-1]
        distsite[5] = args.reldir
        distsite.append(f'{args.version}')
        distsite = '/'.join(distsite)
        distdir = f'/usr/freebsd-dist-{args.version}'
        print('distsite:', distsite)
        print('distdir:', distdir)
        os.makedirs(distdir, exist_ok=True)
        env['BSDINSTALL_DISTDIR'] = distdir
        env['BSDINSTALL_DISTSITE'] = distsite
    else:
        version = focker_subprocess_check_output('freebsd-version').split().decode('utf-8')
        distdir = env.get('BSDINSTALL_DISTDIR', '/usr/freebsd-dist')

    if args.interactive:
        sha256 = None
    else:
        sha256 = hashlib.sha256(('FreeBSD ' + version).encode('utf-8')).hexdigest()
    im = Image.create(sha256=sha256)

    try:
        if args.interactive:
            focker_subprocess_run(['bsdinstall', 'jail', im.mountpoint], env=env)
        else:
            focker_subprocess_run(['focker-bsdinstall', im.mountpoint], env=env)
    except CalledProcessError:
        im.destroy()
        raise

    if args.cleandist:
        shutil.rmtree(distdir)

    tags = args.tags
    if tags is None:
        tags = [ 'freebsd-latest', f'freebsd-{version.split("-")[0]}']
    im.add_tags(tags)

    print('Created', im.name, 'mounted at', im.mountpoint, 'with tags:', ', '.join(im.tags))