import importlib
import pkgutil


class Plugins:
    def __init__(self):
        self.discovered_plugins = {
            name: importlib.import_module(name)
            for finder, name, ispkg
            in pkgutil.iter_modules()
            if name.startswith('focker_')
        }

    def run(self, func_name, *args, **kwargs):
        for _, plug in self.discovered_plugins.items():
            if hasattr(plug, func_name):
                getattr(plug, func_name)(*args, **kwargs)

    def notify(self, event_name, *args, **kwargs):
        func_name = 'on_' + event_name
        return self.run(func_name, *args, **kwargs)
