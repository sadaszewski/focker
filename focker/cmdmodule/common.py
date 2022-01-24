#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from tabulate import tabulate
import argparse
from ..core import JlsCache, \
    ZfsPropertyCache, \
    JailConfCache


DISPLAY_FIELDS = ['name', 'tags', 'sha256', 'mountpoint', 'is_protected',
    'is_finalized', 'size', 'referred_size',
    'origin_tags', 'origin_mountpoint', 'origin_sha256']

DEFAULT_DISPLAY_FIELDS = ['tags', 'size', 'mountpoint']


def standard_fobject_commands(fobject_class,
    display_fields=DISPLAY_FIELDS,
    default_display_fields=DEFAULT_DISPLAY_FIELDS,
    **kwargs):

    return dict(
        list=dict(
            aliases=['lst', 'ls', 'l'],
            func=kwargs.get('list', lambda args: cmd_taggable_list(args, fobject_class)),
            output=dict(
                aliases=['o'],
                type=str,
                default=default_display_fields,
                nargs='+',
                choices=display_fields
            ),
            sort=dict(
                aliases=['s'],
                type=str,
                default=None,
                choices=display_fields
            ),
            tagged=dict(
                aliases=['t'],
                action='store_true'
            )
        ),
        create=dict(
            aliases=['creat', 'crea', 'cre', 'c'],
            func=kwargs.get('create', lambda args: cmd_fobject_create(args, fobject_class)),
            tags=dict(
                aliases=['t'],
                type=str,
                nargs='+'
            )
        ),
        prune=dict(
            aliases=['pru', 'p'],
            func=kwargs.get('prune', lambda args: cmd_fobject_prune(args, fobject_class))
        ),
        tag=dict(
            aliases=['t'],
            func=kwargs.get('tag', lambda args: cmd_fobject_tag(args, fobject_class)),
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
            func=kwargs.get('untag', lambda args: cmd_fobject_untag(args, fobject_class)),
            tags=dict(
                positional=True,
                nargs='+'
            )
        ),
        remove=dict(
            aliases=['rm', 'r'],
            func=kwargs.get('remove', lambda args: cmd_fobject_remove(args, fobject_class)),
            reference=dict(
                positional=True,
                type=str
            ),
            force=dict(
                action='store_true'
            )
        ),
        set=dict(
            func=kwargs.get('set', lambda args: cmd_fobject_set(args, fobject_class)),
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
            func=kwargs.get('get', lambda args: cmd_fobject_get(args, fobject_class)),
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
            func=kwargs.get('protect', lambda args: cmd_fobject_protect(args, fobject_class)),
            reference=dict(
                positional=True,
                type=str
            )
        ),
        unprotect=dict(
            aliases=['unp'],
            func=kwargs.get('unprotect', lambda args: cmd_fobject_unprotect(args, fobject_class)),
            reference=dict(
                positional=True,
                type=str
            )
        )
    )


def cmd_taggable_list(args, tcls):
    with ZfsPropertyCache(), \
        JlsCache(), \
        JailConfCache():
        
        lst = tcls.list()
        if args.tagged:
            lst = [ t for t in lst if t.tags ]
        def to_string(s):
            if s is None:
                return '-'
            elif isinstance(s, bool):
                return 'on' if s else 'off'
            elif isinstance(s, set):
                return ', '.join(s) if s else '-'
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
    o.destroy(force=args.force)


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
