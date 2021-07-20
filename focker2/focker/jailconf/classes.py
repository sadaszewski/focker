from .misc import flatten


def quote_value(s):
    if isinstance(s, list):
        return ','.join(quote_value(x) for x in s)

    s = str(s)

    try:
        _ = int(s)
        return s
    except:
        pass

    if '\'' in s or '"' in s or '\\' in s or ' ' in s or '\t' in s or '\r' in s or '\n' in s:
        s = s.replace('\n', '\\n')
        s = s.replace('\r', '\\r')
        s = s.replace('\t', '\\t')
        s = s.replace('\\', '\\\\')
        s = s.replace('\'', '\\\'')
        s = '\'' + s + '\''

    return s


class KeyValuePair:
    def __init__(self, toks):
        self.toks = toks

    @property
    def key(self):
        return self.toks[1]

    @property
    def value(self):
        return self.toks[5]

    def __repr__(self):
        return f'KeyValuePair({self.toks})'

    def __str__(self):
        return flatten([ self.toks[0], quote_value(self.key) ] + self.toks[2:5] +
            [ quote_value(self.value) ] + self.toks[6:])


class KeyValueAppendPair:
    def __init__(self, toks):
        self.toks = toks

    @property
    def key(self):
        return self.toks[1]

    @property
    def value(self):
        return self.toks[5]

    def __repr__(self):
        return f'KeyValueAppendPair({self.toks})'

    def __str__(self):
        return flatten([ self.toks[0], quote_value(self.key) ] + self.toks[2:5] +
            [ quote_value(self.value) ] + self.toks[6:])


class KeyValueToggle:
    def __init__(self, toks):
        self.toks = toks

    @property
    def key(self):
        k = self.toks[1].split('.')
        if k[-1].startswith('no'):
            return '.'.join(k[:-1] + [ k[-1][2:] ])
        else:
            return '.'.join(k)

    @property
    def value(self):
        k = self.toks[1].split('.')
        if k[-1].startswith('no'):
            return False
        else:
            return True

    def __str__(self):
        return flatten(self.toks)


class JailBlock:
    def __init__(self, toks):
        self.sp_1, self.jail_name, self.sp_2, self.curly_open, \
            self.statements, self.sp_3, self.curly_close = toks
        if not isinstance(self.statements, list):
            self.statements = self.statements.asList()

    @classmethod
    def create(cls, jail_name):
        return cls([ '\n', jail_name, ' ', '{', [], '\n', '}' ])

    @property
    def name(self):
        return self.jail_name

    def set_key(self, name, value):
        self.statements.append(KeyValuePair(
            [ '\n  ', name, '', '=', '', value, '', ';' ]
        ))

    def get_key(self, name):
        res = []
        for s in self.statements:
            if isinstance(s, KeyValuePair) and s.key == name:
                res = [ s.value ]
            elif isinstance(s, KeyValueAppendPair) and s.key == name:
                if isinstance(s.value, list):
                    res += s.value
                else:
                    res.append(s.value)
            elif isinstance(s, KeyValueToggle) and s.key == name:
                res = [ s.value ]
        if len(res) == 0:
            raise KeyError
        if len(res) == 1:
            return res[0]
        return res

    def has_key(self, name):
        try:
            _ = self.get_key(name)
        except KeyError:
            return False
        return True

    def remove_key(self, name):
        if not self.has_key(name):
            raise KeyError
        self.statements = [ s for s in self.statements \
            if s.__class__ not in [ KeyValuePair, KeyValueAppendPair, KeyValueToggle ] \
            or s.key != name ]

    def __str__(self):
        return flatten([ self.sp_1, self.jail_name, self.sp_2 + self.curly_open, \
            self.statements, self.sp_3, self.curly_close ])


class JailConf:
    def __init__(self, toks):
        self.toks = toks[0].asList()
        self.trailing_space = toks[1]

    @property
    def statements(self):
        return self.toks

    def get_jail_block(self, x):
        for s in self.statements:
            if isinstance(s, JailBlock):
                if s.name == x:
                    return s
        raise KeyError

    def has_jail_block(self, x):
        try:
            _ = self.get_jail_block(x)
            return True
        except KeyError:
            return False

    def remove_jail_block(self, x):
        if not self.has_jail_block(x):
            raise KeyError
        self.toks = [ t for t in toks if not isinstance(t, JailBlock) or t.name != x ]

    def add_statement(self, x):
        self.toks.append(x)

    def __str__(self):
        return flatten([ self.toks, self.trailing_space ])
