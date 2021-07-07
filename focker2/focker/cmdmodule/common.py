from tabulate import tabulate


def cmd_taggable_list(args, tcls):
    lst = tcls.list()
    def to_string(s):
        if isinstance(s, bool):
            return 'on' if s else 'off'
        elif isinstance(s, set):
            return ', '.join(s)
        else:
            return str(s)
    res = [ [ to_string(getattr(t, o)) for o in args.output  ] for t in lst ]
    headers = [ o[0].upper() + o[1:].replace('_', ' ') for o in args.output ]
    if args.sort is not None:
        key = [ to_string(getattr(t, args.sort)) for t in lst ]
        order = sorted(range(len(lst)), key=lambda i: key[i])
        res = [ res[i] for i in order ]
    # res = [ (' '.join(im.tags), im.mountpoint, ) for im in Image.list() ]
    print(tabulate(res, headers))
