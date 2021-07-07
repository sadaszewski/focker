from .command import create_parser, \
    run_command


def main():
    parser = create_parser()
    args = parser.parse_args()
    run_command(args)


if __name__ == '__main__':
    main()
