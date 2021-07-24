from ...core import focker_subprocess_run, \
    CalledProcessError, \
    Image


def cmd_bootstrap_install(args):
    im = Image.create()

    if args.version:
        raise NotImplementedError

    try:
        if args.interactive:
            focker_subprocess_run(['bsdinstall', 'jail', im.mountpoint)
        else:
            focker_subprocess_run(['focker-bsdinstall', im.mountpoint])
    except CalledProcessError:
        im.destroy()
        raise

    im.add_tags(args.tags)

    print('Created', im.name, 'mounted at', im.mountpoint, 'tags:', im.tags)
