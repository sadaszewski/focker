from focker.plugin import Plugin, \
    PLUGIN_MANAGER
from focker.__main__ import main
from contextlib import redirect_stdout
import io


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
