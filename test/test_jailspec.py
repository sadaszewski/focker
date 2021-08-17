from focker.core.jailspec import JailSpec
from focker.core.jailspec.variants import *
import pytest


class TestJailSpec:
    def test01_not_factory_method(self):
        with pytest.raises(RuntimeError, match='factory methods'):
            _ = JailSpec()

    def test02_unknown_parameter(self):
        with pytest.raises(KeyError, match='Unknown parameter'):
            JailSpec.validate_dict({ 'this parameter you surely cannot know': 1 })

    def test03_exec_start_command_exclusive(self):
        with pytest.raises(KeyError, match='exclusive'):
            JailSpec.validate_dict({ 'exec.start': 'foo', 'command': 'bar' })

    def test04_exec_user_exclusive(self):
        with pytest.raises(KeyError, match='exclusive'):
            JailSpec.validate_dict({ 'exec.jail_user': 'nobody', 'exec.system_jail_user': 'nobody' })

    def test05_no_path(self):
        with pytest.raises(KeyError, match='Path not specified'):
            JailSpec.validate_dict({})

    def test05_path_not_exist(self):
        with pytest.raises(RuntimeError, match='does not exist'):
            JailSpec.validate_dict({ 'path': 'there is no chance that this path exists' })

    def test06_resolv_conf_wrong(self):
        with pytest.raises(RuntimeError, match='resolv_conf'):
            JailSpec.validate_dict({ 'path': '/', 'resolv_conf': 'foo' })
        with pytest.raises(RuntimeError, match='resolv_conf'):
            JailSpec.validate_dict({ 'path': '/', 'resolv_conf': { 'file': 'foo', 'system_file': 'bar' } })
        with pytest.raises(RuntimeError, match='resolv_conf'):
            JailSpec.validate_dict({ 'path': '/', 'resolv_conf': { 'foo': 'bar' } })

    def test07_variants_no_image_spec(self):
        with pytest.raises(KeyError, match='Image'):
            CloneImageJailSpec.from_dict({})

    def test07_variants_image_in_spec_raise(self):
        with pytest.raises(KeyError, match='separately'):
            OneExecJailSpec.from_image_and_dict(None, { 'image': 'abc' })
        with pytest.raises(KeyError, match='separately'):
            ImageBuildJailSpec.from_image_and_dict(None, { 'image': 'abc' })
