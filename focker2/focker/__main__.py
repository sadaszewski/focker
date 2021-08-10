from .command import create_parser
from .plugin import PLUGIN_MANAGER
from .misc import FockerLock
import sys


@FockerLock()
def main(args=None):
    PLUGIN_MANAGER.load()
    parser = create_parser()
    args = parser.parse_args(args)
    if not hasattr(args, 'func'): # pragma: no cover
        parser.print_usage()
        sys.exit('You must choose an action')
    args.func(args)


if __name__ == '__main__':
    main() # pragma: no cover
