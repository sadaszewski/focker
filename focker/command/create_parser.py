#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from argparse import ArgumentParser
from ..plugin import PLUGIN_MANAGER
import os
from ..misc import merge_dicts
from ..core import FOCKER_CONFIG
from .materialize_parsers import materialize_parsers


def create_parser():
    parser = ArgumentParser('focker')
    subp = parser.add_subparsers()

    provided_parsers = {}
    for p in PLUGIN_MANAGER.discovered_plugins:
        provided_parsers.update(p.provide_parsers())

    for p in PLUGIN_MANAGER.discovered_plugins:
        # print('Extending parsers with:', p.extend_parsers())
        provided_parsers = merge_dicts(provided_parsers, p.extend_parsers())

    # print('provided_parsers:', list(provided_parsers.keys()))

    materialize_parsers(provided_parsers, subp, FOCKER_CONFIG.command.overrides)

    return parser
