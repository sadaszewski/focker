from .misc import flatten, \
    quote_value


class Value:
    def __init__(self, toks):
        if isinstance(toks, list):
            assert len(toks) == 0
            self.value = self.toks[0]
        else:
            self.value = toks

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value})'

    def __str__(self):
        return quote_value(self.value)


class Key(Value):
    pass


class KeyValuePair:
    def __init__(self, toks):
        self.toks = flatten(toks)

    @property
    def key(self):
        return [ k for k in self.toks if isinstance(k, Key) ][0].key

    @property
    def value(self):
        return [ v for v in self.toks if isinstance(v, Value)][0].value

    def __repr__(self):
        return f'KeyValuePair({self.toks})'

    def __str__(self):
        return ''.join(str(t) for t in self.toks)


class KeyValueAppendPair:
    def __init__(self, toks):
        self.toks = flatten(toks)

    @property
    def key(self):
        return [ k for k in self.toks if isinstance(k, Key) ][0].key

    @property
    def value(self):
        return [ v for v in self.toks if isinstance(v, Value)][0].value

    def __repr__(self):
        return f'KeyValueAppendPair({self.toks})'

    def __str__(self):
        return ''.join(str(t) for t in self.toks)


class KeyValueToggle:
    def __init__(self, toks):
        self.toks = flatten(toks)

    @property
    def key(self):
        k = [ k for k in self.toks if isinstance(k, Key) ][0].key
        k = k.split('.')
        if k[-1].startswith('no'):
            return '.'.join(k[:-1] + [ k[-1][2:] ])
        else:
            return '.'.join(k)

    @property
    def value(self):
        k = [ k for k in self.toks if isinstance(k, Key) ][0].key
        k = k.split('.')
        if k[-1].startswith('no'):
            return False
        else:
            return True

    def __repr__(self):
        return f'KeyValueToggle({self.toks})'

    def __str__(self):
        return ''.join(str(t) for t in self.toks)


class JailName(Value):
    pass


class Statements(list):
    pass


class JailBlock:
    def __init__(self, toks):
        self.toks = toks

    @classmethod
    def create(cls, jail_name):
        return cls([ '\n', JailName(jail_name), ' {', Statements(), '\n}' ])

    @property
    def name(self):
        return [ n for n in self.toks if isinstance(n, JailName) ][0].value

    @property
    def statements(self):
        return [ s for s in self.toks if isinstance(s, Statements)][0]

    def set_key(self, name, value):
        if isinstance(value, bool):
            self.toggle_key(name, value)
            return

        self.statements.append(KeyValuePair(
            [ '\n  ', Key(name), '=', Value(value), ';' ]
        ))

    def append_key(self, name, value):
        if isinstance(value, bool):
            self.toggle_key(name, value)
            return

        self.statements.append(KeyValueAppendPair(
            [ '\n  ', Key(name), '+=', Value(value), ';' ]
        ))

    def toggle_key(self, name, value):
        if not value:
            name = name.split('.')
            name = '.'.join(name[:-1] + [ 'no' + name[-1] ])

        self.statements.append(KeyValueToggle([ '\n  ', Key(name), ';' ]))

    def get_key(self, name):
        res = []
        for s in self.statements:
            if isinstance(s, KeyValuePair) and s.key == name:
                res = s.value if isinstance(s.value, list) else [ s.value ]
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
        return ''.join(str(t) for t in self.toks)


class JailConf:
    def __init__(self, toks=[]):
        self.toks = flatten(toks)

    @property
    def statements(self):
        return [ t for t in self.tok \
            if t.__class__ in [ KeyValuePair, KeyValueAppendPair, KeyValueToggle, JailBlock ] ]

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
        self.toks = [ t for t in self.toks if not isinstance(t, JailBlock) or t.name != x ]

    def add_statement(self, x):
        self.toks.append(x)

    def __str__(self):
        return ''.join(str(t) for t in self.toks)
