from focker.core.jailspec import JailSpec
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
