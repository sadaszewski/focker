def materialize_parsers(defs, subp, overrides, hook_name=[]):
    for k, v in defs.items():
        o = overrides.get(k, {})
        # print(k, v.get('aliases', []))
        parser = subp.add_parser(k, aliases=v.get('aliases', []))
        if ('subparsers' in v) + ('func' in v) != 1:
            raise KeyError('Exactly one of "subparsers" or "func" must be specified')
        if 'subparsers' in v:
            materialize_parsers(v['subparsers'], parser.add_subparsers(), o, hook_name + [ k ])
        elif 'func' in v:
            parser.set_defaults(func=v['func'], hook_name='.'.join(hook_name + [ k ]))
            for k_1, v_1 in v.items():
                if k_1 in ['func', 'aliases']:
                    continue
                v_2 = { k: v for k, v in v_1.items()
                    if k not in [ 'aliases', 'positional' ]}
                if k_1 in o:
                    v_2['default'] = o[k_1].split(',') \
                        if ',' in o[k_1] else o[k_1]
                if v_1.get('positional', False):
                    parser.add_argument(k_1, **v_2)
                else:
                    parser.add_argument(f'--{k_1.replace("_", "-")}',
                        *[ f'-{a}' for a in v_1.get('aliases', []) ],
                        **v_2)
