#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from .osjail import OSJail


class TemporaryOSJail(OSJail):
    def __init__(self, spec, create_started=True, **kwargs):
        super().__init__(init_key=OSJail._init_key, name=None)

        self.spec = spec
        self.create_started = create_started

        self.ospec = None
        self.osjail = None

    def __enter__(self):
        from ..osjailspec import OSJailSpec
        self.ospec = OSJailSpec.from_jailspec(self.spec)
        self.ospec.add()
        self.name = self.ospec.name
        if self.create_started:
            self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.create_started:
            self.stop()
        self.ospec.remove()
