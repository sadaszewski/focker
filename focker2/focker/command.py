from argparse import ArgumentParser
from .plugin import PLUGIN_MANAGER


def create_parser():
    parser = ArgumentParser('focker')
    subp = parser.add_subparsers()
    for p in PLUGIN_MANAGER.discovered_plugins:
        for m in p.provide_command_modules():
            m.provide_parsers(subp)
    return parser
