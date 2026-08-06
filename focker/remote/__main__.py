from argparse import ArgumentParser
import os
import sys
import logging
from ..command import materialize_parsers, CommandConfig
from . import image, volume, compose
from ..misc import merge_dicts
from functools import reduce
from .client import setup_client, forward_command


PARSER_DEFS = reduce(merge_dicts, [
    image.PARSERS,
    volume.PARSERS,
    compose.PARSERS,
])


def create_parser():
    parser = ArgumentParser(allow_abbrev=False)
    subp = parser.add_subparsers()

    command_config = CommandConfig()

    materialize_parsers(PARSER_DEFS, subp, command_config.overrides)

    return parser


def setup_logging():
    if "FOCKER_REMOTE_LOG_LEVEL" in os.environ:
        log_level = os.environ["FOCKER_REMOTE_LOG_LEVEL"]
        if log_level.upper() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            log_level = getattr(logging, log_level.upper())
            logging.basicConfig(level=log_level)
        else:
            raise ValueError("Unrecognized log level specified in FOCKER_REMOTE_LOG_LEVEL")
    logger = logging.getLogger("focker.remote")
    return logger


def main():
    parser = create_parser()

    for k, v in PARSER_DEFS.items():
        if sys.argv[1] == k or sys.argv[1] in v.get("aliases", []):
            args = parser.parse_args()
            args.func(args)
            return

    if "-h" in sys.argv[1:] or "--help" in sys.argv[1:]:
        parser.print_help()
        forward_command(setup_client())
        return

    forward_command(setup_client())


if __name__ == "__main__":
    main()
