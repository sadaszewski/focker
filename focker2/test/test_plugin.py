from focker.plugin import Plugin


class TestPlugin:
    def test01_empty_plugin(self):
        p = Plugin()
        assert p.provide_parsers() == {}
        assert p.extend_parsers() == {}
        assert p.change_defaults() == {}
        assert p.install_pre_hooks() == {}
        assert p.install_post_hooks() == {}
