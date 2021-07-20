def flatten(x):
    try:
        it = iter(x)
    except TypeError:
        return str(x)
    if isinstance(it, iter([]).__class__):
        return ''.join([ flatten(y) for y in x ])
    else:
        return str(x)
