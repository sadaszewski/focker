#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


import ruamel.yaml as yaml


def safe_load(stream):
    return yaml.YAML(typ='safe', pure=True).load(stream)


def safe_dump(obj, stream):
    return yaml.YAML(typ='safe', pure=True).dump(obj, stream)
