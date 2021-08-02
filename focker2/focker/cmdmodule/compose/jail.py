from ...core import CloneImageJailSpec, \
    OSJailSpec, \
    JailFs, \
    OSJail


def build_jails(spec):
    for tag, jspec in spec.items():
        jfs = JailFs.from_tag(tag, raise_exc=False)
        if jfs is not None:
            jfs.destroy()

        jspec = CloneImageJailSpec.from_dict(jspec)
        jspec.jfs.add_tags([ tag ])
        ospec = OSJailSpec.from_jailspec(jspec)
        ospec.add()
