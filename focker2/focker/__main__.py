from .command import create_parser
from .plugin import PLUGIN_MANAGER
import sys


def main():
    PLUGIN_MANAGER.load()
    parser = create_parser()
    args = parser.parse_args()
    if not hasattr(args, 'func'):
        parser.print_usage()
        sys.exit('You must choose an action')
    args.func(args)


if __name__ == '__main__':
    main()
