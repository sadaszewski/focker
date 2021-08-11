from ...core import CloneImageJailSpec, \
    OSJailSpec, \
    JailFs, \
    OSJail


def build_jails(spec):
    print('Removing existing jails...')
    for tag, _ in spec.items():
        jfs = JailFs.from_tag(tag, raise_exc=False)
        if jfs is not None:
            jfs.destroy()

    print('Building new jails...')
    for tag, jspec in spec.items():
        jspec = CloneImageJailSpec.from_dict(jspec)
        jspec.jfs.add_tags([ tag ])
        ospec = OSJailSpec.from_jailspec(jspec)
        ospec.add()
