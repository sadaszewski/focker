import re
from functools import reduce


def flatten(x):
    try:
        it = iter(x)
    except TypeError:
        return [ x ]
    if isinstance(it, iter([]).__class__):
        return reduce(list.__add__, [ flatten(y) for y in x ], [])
    else:
        return [ x ]


def quote_value(s):
    if isinstance(s, list):
        return ','.join(quote_value(x) for x in s)

    if isinstance(s, bool):
        return str(s).lower()

    s = str(s)

    if s.isnumeric():
        return s

    if not re.match('^[a-zA-Z0-9.\-_]*$', s):
        s = s.encode('unicode_escape').decode('utf-8')
        s = s.replace('\'', '\\\'')
        s = '\'' + s + '\''

    return s
