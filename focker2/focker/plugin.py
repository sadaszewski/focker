import importlib
import pkgutil
from .core import FOCKER_CONFIG
from .misc import merge_dicts


class Plugin:
    @staticmethod
    def provide_parsers():
        return {}

    @staticmethod
    def extend_parsers():
        return {}

    @staticmethod
    def change_defaults():
        return {}

    @staticmethod
    def install_pre_hooks():
        return {}

    @staticmethod
    def install_post_hooks():
        return {}


class PluginManager:
    def __init__(self):
        self.discovered_modules = {}
        self.discovered_plugins = []

    def load(self):
        self.discovered_modules = {
            name: importlib.import_module(name)
            for finder, name, ispkg
            in pkgutil.iter_modules()
            if name == 'focker' or name.startswith('focker_')
        }
        for m in self.discovered_modules.values():
            for k, v in m.__dict__.items():
                if k.endswith('Plugin') and issubclass(v, Plugin):
                    self.discovered_plugins.append(v)

    def change_defaults(self):
        for p in self.discovered_plugins:
            for k, v in p.change_defaults().items():
                subsys, entrynam = k.split('.')
                if not hasattr(FOCKER_CONFIG, subsys):
                    raise KeyError(f'Unrecognized config subsystem: "{subsys}"')
                subsys = getattr(FOCKER_CONFIG, subsys)
                if not hasattr(subsys, entrynam):
                    raise KeyError(f'Unrecognized entry name: "{entrynam}" in config subsystem "{subsys}"')
                old_v = getattr(subsys, entrynam)
                setattr(subsys, entrynam, merge_dicts(old_v, v))

    def execute_pre_hooks(self, hook_name, args):
        for p in self.discovered_plugins:
            for hn, hf in p.install_pre_hooks().items():
                if hn != hook_name:
                    continue
                hf(args)

    def execute_post_hooks(self, hook_name, args):
        for p in self.discovered_plugins:
            for hn, hf in p.install_post_hooks().items():
                if hn != hook_name:
                    continue
                hf(args)


PLUGIN_MANAGER = PluginManager()
