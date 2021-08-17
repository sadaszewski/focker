from focker.core.osjailspec import *
from focker.core.jailspec import JailSpec
import pytest


class TestOSJailSpec:
    def test01_env_var_with_spaces(self):
        with pytest.raises(ValueError, match='spaces'):
            _ = gen_env_command('ls -al', { 'name with spaces': 'foo' })

    def test02_concat_commands(self):
        assert concat_commands([ 'a', 'b', 'c' ]) == 'a && b && c'
        assert concat_commands('a') == 'a'

    def test03_not_fac_meth_raise(self):
        with pytest.raises(RuntimeError, match='factory methods'):
            _ = OSJailSpec()

    def test04_resolv_conf_file(self):
        spec = JailSpec.from_dict({ 'name': 'focker_unit_test_osjailspec',
            'path': '/tmp', 'resolv_conf': { 'file': '/some/dummy/resolv.conf' } })
        ospec = OSJailSpec.from_jailspec(spec)
        assert 'ln -s /some/dummy/resolv.conf /etc/resolv.conf' in ospec.params['exec.start']
        # print(ospec.params)

    def test05_resolv_conf_system_file(self):
        spec = JailSpec.from_dict({ 'name': 'focker_unit_test_osjailspec',
            'path': '/tmp', 'resolv_conf': { 'system_file': '/system/dummy/resolv.conf' } })
        ospec = OSJailSpec.from_jailspec(spec)
        assert 'cp /system/dummy/resolv.conf /tmp/etc/resolv.conf' in ospec.params['exec.prestart']

    def test06_resolv_conf_image(self):
        spec = JailSpec.from_dict({ 'name': 'focker_unit_test_osjailspec',
            'path': '/tmp', 'resolv_conf': 'image' })
        ospec = OSJailSpec.from_jailspec(spec)
        assert '/etc/resolv.conf' not in ospec.params['exec.prestart']
        assert '/etc/resolv.conf' not in ospec.params['exec.start']

    def test07_wrong_resolv_conf(self):
        spec = JailSpec.from_dict({ 'name': 'focker_unit_test_osjailspec',
            'path': '/tmp', 'resolv_conf': 'image' })
        spec.resolv_conf = 'foo'
        with pytest.raises(ValueError, match='resolv_conf'):
            ospec = OSJailSpec.from_jailspec(spec)

    def test08_to_dict(self):
        spec = JailSpec.from_dict({ 'name': 'focker_unit_test_osjailspec',
            'path': '/tmp', 'resolv_conf': 'image' })
        ospec = OSJailSpec.from_jailspec(spec)
        assert ospec.to_dict() == ospec.params

    def test09_command(self):
        spec = JailSpec.from_dict({ 'name': 'focker_unit_test_osjailspec',
            'path': '/tmp', 'command': 'ls -al', 'exec.start': { '__delete__': True } })
        ospec = OSJailSpec.from_jailspec(spec)
        assert 'command' not in ospec.params
        assert 'exec.start' in ospec.params
        assert ospec.params['exec.start'] == 'ls -al'
