#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


import importlib
import importlib.metadata
import pkgutil
from .core import FOCKER_CONFIG
from .misc import merge_dicts
from functools import reduce


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
        self.discovered_distributions = {}
        self.discovered_modules = {}
        self.discovered_plugins = []

    def load(self):
        self.discovered_distributions = {
            d.name: importlib.import_module(d.name)
            for d in importlib.metadata.distributions()
            if d.name == 'focker' or d.name.startswith('focker_')
        }

        self.discovered_modules = dict(reduce(list.__add__, [
            [
                (p.name, importlib.import_module(p.name))
                for p in pkgutil.walk_packages(d.__path__, prefix=f"{d.__name__}.", onerror=lambda _: None)
            ] for d in self.discovered_distributions.values()
        ]))
        self.discovered_modules.update(self.discovered_distributions)

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
