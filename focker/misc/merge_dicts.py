#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


class DeleteMe:
    pass


def merge_dicts(a, b):
    if isinstance(a, dict):
        if not isinstance(a, type(b)) and not isinstance(b, type(a)): # type(a) != type(b):
            raise TypeError('%s != %s' % ( type(a), type(b) ))

        if '__delete__' in b and b['__delete__']:
            return DeleteMe

        if '__replace__' in b and b['__replace__']:
            b = b.__class__(b)
            del b['__replace__']
            return b

        a = a.__class__(a)

        for k, v in b.items():
            tmp = merge_dicts(a[k], b[k]) \
                if k in a else b[k]
            if tmp == DeleteMe:
                del a[k]
            else:
                a[k] = tmp
        return a
    #elif type(a) == list:
    #    if type(a) != type(b):
    #        raise ValueError
    #    return a + b
    else:
        if isinstance(b, dict) and '__delete__' in b and b['__delete__']:
            return DeleteMe
        return b
