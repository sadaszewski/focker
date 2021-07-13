from tabulate import tabulate


def standard_fobject_commands(fobject_class,
    display_fields=['name', 'tags', 'sha256', 'mountpoint', 'is_protected', 'is_finalized']):

    return dict(
        list=dict(
            aliases=['lst', 'ls', 'l'],
            cmd=lambda args: cmd_taggable_list(args, fobject_class),
            output=dict(
                aliases=['o'],
                type=str,
                default=['tags', 'mountpoint'],
                nargs='+',
                choices=display_fields
            ),
            sort=dict(
                aliases=['s'],
                type=str,
                default=None,
                choices=display_fields
            )
        ),
        create=dict(
            aliases=['creat', 'crea', 'cre', 'c'],
            func=lambda args: cmd_fobject_create(args, fobject_class),
            tags=dict(
                aliases=['t'],
                type=str,
                nargs='+'
            )
        ),
        prune=dict(
            aliases=['pru', 'p'],
            func=lambda args: cmd_fobject_prune(args, fobject_class)
        ),
        tag=dict(
            aliases=['t'],
            func=lambda args: cmd_fobject_tag(args, fobject_class),
            reference=dict(
                positional=True,
                type=str
            ),
            tags=dict(
                positional=True,
                type=str,
                nargs='+'
            )
        ),
        untag=dict(
            aliases=['u'],
            func=lambda args: cmd_fobject_untag(args, fobject_class),
            tags=dict(
                positional=True,
                nargs='+'
            )
        ),
        remove=dict(
            aliases=['rm', 'r'],
            func=lambda args: cmd_fobject_remove(args, fobject_class),
            reference=dict(
                positional=True,
                type=str
            )
        ),
        set=dict(
            func=lambda args: cmd_fobject_set(args, fobject_class),
            reference=dict(
                positional=True,
                type=str
            ),
            properties=dict(
                positional=True,
                type=str,
                nargs=argparse.REMAINDER
            )
        ),
        get=dict(
            func=lambda args: cmd_fobject_get(args, fobject_class),
            reference=dict(
                positional=True,
                type=str
            ),
            properties=dict(
                positional=True,
                type=str,
                nargs=argparse.REMAINDER
            )
        ),
        protect=dict(
            aliases=['pro'],
            func=lambda args: cmd_fobject_protect(args, fobject_class),
            reference=dict(
                positional=True,
                type=str
            )
        ),
        unprotect=dict(
            aliases=['unp'],
            func=lambda args: cmd_fobject_unprotect(args, fobject_class),
            reference=dict(
                positional=True,
                type=str
            )
        )
    )


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


def cmd_fobject_create(args, fobject_class):
    o = fobject_class.create()
    o.add_tags(args.tags)
    print('Created', o.name, 'mounted at', o.path)


def cmd_fobject_prune(args, fobject_class):
    fobject_class.prune()


def cmd_fobject_tag(args, fobject_class):
    o = fobject_class.from_any_id(args.reference)
    o.add_tags(args.tags)


def cmd_fobject_untag(args, fobject_class):
    fobject_class.untag(args.tags)


def cmd_fobject_remove(args, fobject_class):
    o = fobject_class.from_any_id(args.reference)
    o.destroy()


def cmd_fobject_set(args, fobject_class):
    o = fobject_class.from_any_id(args.reference)
    if not args.properties:
        raise ValueError('You must specify some properties')
    props = { p.split('=')[0]: '='.join(p.split('=')[1:]) for p in args.properties }
    o.set_props(props)


def cmd_fobject_get(args, fobject_class):
    o = fobject_class.from_any_id(args.reference)
    if not args.properties:
        raise ValueError('You must specify some properties')
    res = o.get_props(args.properties)
    res = [ [ k, res[k] ] for k in args.properties ]
    print(tabulate(res, headers=['Property', 'Value']))


def cmd_fobject_protect(args, fobject_class):
    o = fobject_class.from_any_id(args.reference)
    o.protect()


def cmd_fobject_unprotect(args, fobject_class):
    o = fobject_class.from_any_id(args.reference)
    o.unprotect()
