from focker.core import OSJail, \
    OSJailSpec, \
    JailFs, \
    clone_image_jailspec, \
    Volume
from focker.core.jailspec import JailSpec
import pytest
import os
import focker.core.osjail as osjail
import json
from contextlib import ExitStack


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
        with clone_image_jailspec({ 'image': 'freebsd-latest' }) as (spec, jfs, _):
            ospec = OSJailSpec.from_jailspec(spec)
            jail = ospec.add()
            jail.start()
            res = jail.check_output(['ls', '-al']).decode('utf-8')
            jail.stop()
            res = res.split('\n')
            res = [ ln for ln in res if 'bin' in ln or 'var' in ln or 'usr' in ln ]
            assert len(res) == 5

    def test04_jls(self):
        with clone_image_jailspec({ 'image': 'freebsd-latest' }) as (spec, jfs, _):
            ospec = OSJailSpec.from_jailspec(spec)
            jail = ospec.add()
            jail.start()
            res = jail.jls()
            assert res['name'] == jail.name
            jail.stop()

    def test05_factory_methods(self):
        with pytest.raises(RuntimeError, match='factory methods'):
            _ = OSJail()

    def test06_name_not_found(self):
        with pytest.raises(RuntimeError, match='not found'):
            _ = OSJail.from_name('focker-unit-test-impossible-jail-name')

    def test07_mountpoint_not_found(self):
        with pytest.raises(RuntimeError, match='not found'):
            _ = OSJail.from_mountpoint('focker-unit-test-impossible-jail-mountpoint')

    def test08_tag_not_found_noraise(self):
        res = OSJail.from_tag('focker-unit-test-impossible-jail-tag', raise_exc=False)
        assert res is None

    def test09_anyid_not_found_noraise(self):
        res = OSJail.from_any_id('focker-unit-test-impossible-identifier', raise_exc=False)
        assert res is None

    def test10_exec_fib(self):
        with clone_image_jailspec({ 'image': 'freebsd-latest', 'exec.fib': 0 }) as (spec, jfs, _):
            ospec = OSJailSpec.from_jailspec(spec)
            jail = ospec.add()
            jail.start()
            cmd = None
            def dummywrapper(cmd_in, *args, **kwargs):
                nonlocal cmd
                cmd = cmd_in
            jail.jexec(['ls', '-al'], dummywrapper)
            assert 'setfib' in cmd

    def test11_mountpoint_not_found_noraise(self):
        res = OSJail.from_mountpoint('focker-unit-test-impossible-jail-mountpoint', raise_exc=False)
        assert res is None

    def test12_from_tag(self):
        jail, jfs = self._create()
        try:
            jfs.add_tags([ 'focker-unit-test-jail-from-tag' ])
            jail_1 = OSJail.from_tag('focker-unit-test-jail-from-tag')
            assert jail.name == jail_1.name
        finally:
            jfs.destroy()

    def test13_run(self):
        with clone_image_jailspec({ 'image': 'freebsd-latest' }) as (spec, jfs, _):
            ospec = OSJailSpec.from_jailspec(spec)
            jail = ospec.add()
            jail.start()
            jail.run([ 'touch', '/.focker-unit-test-jail-run' ])
            assert os.path.exists(os.path.join(jfs.path, '.focker-unit-test-jail-run'))

    def test14_jls_not_running(self):
        jail, jfs = self._create()
        try:
            with pytest.raises(RuntimeError, match='Not running'):
                _ = jail.jls()
        finally:
            jfs.destroy()

    def test15_multiple_jails_same_name(self, monkeypatch):
        def mock(cmd, *args, **kwargs):
            res = json.dumps({
                'jail-information': dict(
                    jail=[
                        dict(name='focker_focker-unit-test-jail'),
                        dict(name='focker_focker-unit-test-jail')
                    ])
            })
            # print('Mock was called with cmd:', cmd, 'returning:', res)
            return res
        jail, jfs = self._create()
        # print('jail.name:', jail.name)
        try:
            with monkeypatch.context() as m:
                m.setattr(osjail, 'focker_subprocess_check_output', mock)
                with pytest.raises(RuntimeError, match='Multiple jails'):
                    _ = jail.jls()
        finally:
            jfs.destroy()

    def test16_runtime_property(self):
        with clone_image_jailspec({ 'image': 'freebsd-latest' }) as (spec, jfs, _):
            ospec = OSJailSpec.from_jailspec(spec)
            jail = ospec.add()
            jail.start()
            assert jail.has_runtime_property('persist')
            assert jail.get_runtime_property('persist') == True

    def test17_jid(self):
        with clone_image_jailspec({ 'image': 'freebsd-latest' }) as (spec, jfs, _):
            ospec = OSJailSpec.from_jailspec(spec)
            jail = ospec.add()
            assert jail.jid is None
            jail.start()
            assert jail.jid is not None
            jail.stop()
            assert jail.jid is None

    def test18_conf(self):
        jail, jfs = self._create()
        try:
            conf = jail.conf
            assert conf['persist'] == True
        finally:
            jfs.destroy()

    def test19_mount_dest_not_exist(self):
        with ExitStack() as stack:
            v = Volume.create()
            stack.callback(v.destroy)
            spec, jfs, _ = stack.enter_context(clone_image_jailspec({ 'image': 'freebsd-latest',
                'mounts': { v.path: '/a/nested/mount/path/that/wont/exist' } }))
            ospec = OSJailSpec.from_jailspec(spec)
            jail = ospec.add()
            jail.start()
            jail.run([ 'touch', '/a/nested/mount/path/that/wont/exist/.focker-unit-test-osjail' ])
            assert os.path.exists(os.path.join(v.path, '.focker-unit-test-osjail'))
