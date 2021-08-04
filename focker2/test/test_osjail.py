from focker.core import OSJail, \
    OSJailSpec, \
    JailFs
from focker.core.jailspec import JailSpec


class TestOSJail:
    def test01_from_name(self):
        jfs = JailFs.create()
        try:
            spec = JailSpec.from_dict({ 'path': jfs.path, 'name': 'focker-unit-test-jail' })
            ospec = OSJailSpec.from_jailspec(spec)
            ospec.add()
            jail = OSJail.from_name(ospec.name)
        finally:
            jfs.destroy()
