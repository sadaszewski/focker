import re


def flatten(x):
    try:
        it = iter(x)
    except TypeError:
        return [ x ]
    if isinstance(it, iter([]).__class__):
        return reduce(list.__add__, [ flatten(y) for y in x ])
    else:
        return [ x ]


def quote_value(s):
    if isinstance(s, list):
        return ','.join(quote_value(x) for x in s)

    s = str(s)

    try:
        _ = int(s)
        return s
    except:
        pass

    # if '\'' in s or '"' in s or '\\' in s or ' ' in s or '\t' in s or '\r' in s or '\n' in s:
    if not re.match('^[a-zA-Z0-9.\-_]*$', s):
        #s = s.replace('\n', '\\n')
        #s = s.replace('\r', '\\r')
        #s = s.replace('\t', '\\t')
        s = s.replace('\\', '\\\\')
        s = s.replace('\'', '\\\'')
        s = '\'' + s + '\''

    return s
