def quote_for_jailconf(s):
    if isinstance(s, list):
        if len(s) == 0:
            return ''
        elif len(s) == 1:
            return quote_for_jailconf(s[0])
        else:
            return list(map(quote_for_jailconf, s))
    if isinstance(s, bool):
        return s
    if isinstance(s, int):
        return str(s)
    if not isinstance(s, str):
        s = str(s)
    # if '\'' in s or '\\' in s or ' ' in s:
    s = s.replace('\\', '\\\\')
    s = s.replace('\'', '\\\'')
    s = '\'' + s + '\''
    return s


def jailconf_unquote(s):
    if not isinstance(s, str):
        return s
    s = s.strip('\'"')
    s = s.replace('\\\'', '\'')
    s = s.replace('\\\\', '\\')
    return s
