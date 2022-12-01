#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from .command import create_parser
from .plugin import PLUGIN_MANAGER
from .misc import focker_lock
import sys


@focker_lock()
def main(args=None):
    PLUGIN_MANAGER.load()
    PLUGIN_MANAGER.change_defaults()
    parser = create_parser()
    args = parser.parse_args(args)
    if not hasattr(args, 'func'): # pragma: no cover
        parser.print_usage()
        sys.exit('You must choose an action')
    PLUGIN_MANAGER.execute_pre_hooks(args.hook_name, args)
    args.func(args)
    PLUGIN_MANAGER.execute_post_hooks(args.hook_name, args)


if __name__ == '__main__':
    main() # pragma: no cover
