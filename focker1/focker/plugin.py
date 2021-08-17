import importlib
import pkgutil


class Plugins:
    def __init__(self):
        self.discovered_plugins = {}

    def load(self):
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

    def modify(self, value_name, value, frame):
        func_name = 'modify_' + value_name
        def stack_names(frame):
            res = []
            while frame is not None:
                name = frame.f_code.co_name
                if name == 'main':
                    break
                res.append(name)
                frame = frame.f_back
            return reversed(res)
        # print(func_name, value, '.'.join(stack_names(frame)))
        for _, plug in self.discovered_plugins.items():
            if hasattr(plug, func_name):
                value = getattr(plug, func_name)(value, stack_names(frame), frame)
        return value


PLUGINS = Plugins()
