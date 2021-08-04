from focker.core import OSJail, \
    OSJailSpec, \
    JailFs, \
    CloneImageJailSpec
from focker.core.jailspec import JailSpec


class TestOSJail:
    def _create(self):
        jfs = JailFs.create()
        spec = JailSpec.from_dict({ 'path': jfs.path, 'name': 'focker-unit-test-jail' })
        ospec = OSJailSpec.from_jailspec(spec)
        ospec.add()
        jail = OSJail.from_name(ospec.name)
        return jail, jfs

    def test01_from_name(self):
        jfs = JailFs.create()
        try:
            spec = JailSpec.from_dict({ 'path': jfs.path, 'name': 'focker-unit-test-jail' })
            ospec = OSJailSpec.from_jailspec(spec)
            ospec.add()
            jail = OSJail.from_name(ospec.name)
        finally:
            jfs.destroy()

    def test02_from_any_id(self):
        jail, jfs = self._create()
        try:
            jail_1 = OSJail.from_any_id(jfs.sha256)
            assert jail.name == jail_1.name
        finally:
            jfs.destroy()

    def test03_check_output(self):
        spec = CloneImageJailSpec.from_dict({ 'image': 'freebsd-latest' })
        try:
            ospec = OSJailSpec.from_jailspec(spec)
            jail = ospec.add()
            jail.start()
            res = jail.check_output(['ls', '-al']).decode('utf-8')
            jail.stop()
            res = res.split('\n')
            res = [ ln for ln in res if 'bin' in ln or 'var' in ln or 'usr' in ln ]
            assert len(res) == 5
        finally:
            spec.jfs.destroy()

    def test04_jls(self):
        spec = CloneImageJailSpec.from_dict({ 'image': 'freebsd-latest' })
        try:
            ospec = OSJailSpec.from_jailspec(spec)
            jail = ospec.add()
            jail.start()
            res = jail.jls()
            assert res['name'] == jail.name
            jail.stop()
        finally:
            spec.jfs.destroy()
