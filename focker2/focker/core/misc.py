def ensure_list(lst):
    if not isinstance(lst, list):
        return [ lst ]
    return lst
