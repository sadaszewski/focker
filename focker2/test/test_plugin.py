from focker.plugin import Plugin, \
    PLUGIN_MANAGER
from focker.__main__ import main
from contextlib import redirect_stdout, \
    ExitStack
import io
from focker.core import FOCKER_CONFIG
import pytest


class HelloPlugin(Plugin):
    @classmethod
    def say_hello(cls, args):
        print(f'Hello from {cls.__name__}')

    @classmethod
    def say_goodbye(cls, args):
        print(f'Goodbye from {cls.__name__}')


class PreHookPlugin(HelloPlugin):
    @classmethod
    def install_pre_hooks(cls):
        return {
            'jail.list': cls.say_hello,
            'jail.start': cls.say_goodbye
        }


class PostHookPlugin(HelloPlugin):
    @classmethod
    def install_post_hooks(cls):
        return {
            'jail.list': cls.say_hello,
            'jail.start': cls.say_goodbye
        }


class ChangeDefaultsPlugin(Plugin):
    @staticmethod
    def change_defaults():
        return {
            'command.overrides': dict(
                jail=dict(
                    list=dict(
                        output=['name', 'tags', 'mountpoint', 'sha256']
                    )
                )
            )
        }


class ChDefsBadSubsysPlugin(Plugin):
    @staticmethod
    def change_defaults():
        return {
            'xxx.overrides': 1234
        }


class ChDefsBadEntryPlugin(Plugin):
    @staticmethod
    def change_defaults():
        return {
            'command.xxx': 1234
        }


class TestPlugin:
    def test01_empty_plugin(self):
        p = Plugin()
        assert p.provide_parsers() == {}
        assert p.extend_parsers() == {}
        assert p.change_defaults() == {}
        assert p.install_pre_hooks() == {}
        assert p.install_post_hooks() == {}

    def test02_pre_hook(self):
        PLUGIN_MANAGER.discovered_plugins.append(PreHookPlugin)
        cmd = [ 'jail', 'list' ]
        buf = io.StringIO()
        with redirect_stdout(buf):
            main(cmd)
        assert 'Hello from PreHookPlugin' in buf.getvalue()
        assert 'Goodbye' not in buf.getvalue()

    def test03_post_hook(self):
        PLUGIN_MANAGER.discovered_plugins.append(PostHookPlugin)
        cmd = [ 'jail', 'list' ]
        buf = io.StringIO()
        with redirect_stdout(buf):
            main(cmd)
        assert 'Hello from PostHookPlugin' in buf.getvalue()
        assert 'Goodbye' not in buf.getvalue()

    def test04_change_defaults(self):
        with ExitStack() as stack:
            PLUGIN_MANAGER.discovered_plugins.append(ChangeDefaultsPlugin)
            stack.callback(lambda: PLUGIN_MANAGER.discovered_plugins.remove(ChangeDefaultsPlugin))
            cmd = [ 'jail', 'list' ]
            buf = io.StringIO()
            with redirect_stdout(buf):
                main(cmd)
            assert 'Name' in buf.getvalue()
            assert 'Tags' in buf.getvalue()
            assert 'Mountpoint' in buf.getvalue()
            assert 'Sha256' in buf.getvalue()
            assert 'jail' in FOCKER_CONFIG.command.overrides
            assert 'list' in FOCKER_CONFIG.command.overrides['jail']
            assert 'output' in FOCKER_CONFIG.command.overrides['jail']['list']
            assert FOCKER_CONFIG.command.overrides['jail']['list']['output'] == \
                ['name', 'tags', 'mountpoint', 'sha256']

    def test05_chdefs_bad_subsys_raise(self):
        with ExitStack() as stack:
            PLUGIN_MANAGER.discovered_plugins.append(ChDefsBadSubsysPlugin)
            stack.callback(lambda: PLUGIN_MANAGER.discovered_plugins.remove(ChDefsBadSubsysPlugin))
            cmd = [ 'jail', 'list' ]
            with pytest.raises(KeyError, match='Unrecognized config subsystem'):
                main(cmd)

    def test06_chdefs_bad_entry_raise(self):
        with ExitStack() as stack:
            PLUGIN_MANAGER.discovered_plugins.append(ChDefsBadEntryPlugin)
            stack.callback(lambda: PLUGIN_MANAGER.discovered_plugins.remove(ChDefsBadEntryPlugin))
            cmd = [ 'jail', 'list' ]
            with pytest.raises(KeyError, match='Unrecognized entry'):
                main(cmd)
