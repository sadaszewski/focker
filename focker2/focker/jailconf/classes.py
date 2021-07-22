from .misc import flatten, \
    quote_value
import pyparsing as pp


class Value:
    def __init__(self, toks):
        if toks.__class__ in [ list, pp.ParseResults ]:
            assert len(toks) == 1
            self.value = toks[0]
        elif toks.__class__ in [ str, int, bool ]:
            self.value = toks
        elif toks.__class__ == float:
            self.value = str(toks)
        else:
            raise TypeError('Unexpected type')

        if self.value.__class__ == str and self.value.isnumeric():
            self.value = int(self.value)
        elif self.value == 'true':
            self.value = True
        elif self.value == 'false':
            self.value = False

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value})'

    def __str__(self):
        return quote_value(self.value)


class ListOfValues:
    def __init__(self, toks):
        self.toks = flatten(toks)

    @classmethod
    def from_list(cls, lst):
        toks = []
        for i, e in enumerate(lst):
            if i > 0:
                toks.append(', ')
            toks.append(Value(e))
        return cls(toks)

    def __repr__(self):
        return f'ListOfValues({self.toks})'

    def __len__(self):
        return len([ t for t in self.toks if isinstance(t, Value)])

    def __getitem__(self, index):
        if index < 0 or index >= len(self):
            raise IndexError
        return [ t for t in self.toks if isinstance(t, Value) ][index].value

    @property
    def value(self):
        return [ t.value for t in self.toks if isinstance(t, Value) ]

    def __str__(self):
        return ''.join(str(t) for t in self.toks)


class Key(Value):
    pass


class KeyValuePair:
    def __init__(self, toks):
        self.toks = flatten(toks)

    @property
    def key(self):
        return [ k for k in self.toks if k.__class__ == Key ][0].value

    @property
    def value(self):
        return [ v for v in self.toks if v.__class__ in [ Value, ListOfValues ]][0].value

    def __repr__(self):
        return f'KeyValuePair({self.toks})'

    def __str__(self):
        return ''.join(str(t) for t in self.toks)


class KeyValueAppendPair:
    def __init__(self, toks):
        self.toks = flatten(toks)

    @property
    def key(self):
        return [ k for k in self.toks if k.__class__ == Key ][0].value

    @property
    def value(self):
        return [ v for v in self.toks if v.__class__ in [ Value, ListOfValues ]][0].value

    def __repr__(self):
        return f'KeyValueAppendPair({self.toks})'

    def __str__(self):
        return ''.join(str(t) for t in self.toks)


class KeyValueToggle:
    def __init__(self, toks):
        self.toks = flatten(toks)

    @property
    def key(self):
        k = [ k for k in self.toks if k.__class__ == Key ][0].value
        k = k.split('.')
        if k[-1].startswith('no'):
            return '.'.join(k[:-1] + [ k[-1][2:] ])
        else:
            return '.'.join(k)

    @property
    def value(self):
        k = [ k for k in self.toks if k.__class__ == Key ][0].value
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


class Statements:
    def __init__(self, toks=[]):
        self.toks = flatten(toks)

    def __repr__(self):
        return f'Statements({self.toks})'

    def __len__(self):
        return len(self.toks)

    def __getitem__(self, index):
        if index < 0 or index >= len(self):
            raise IndexError
        return self.toks[index]

    def append(self, stmt):
        self.toks.append(stmt)

    def __str__(self):
        return ''.join(str(t) for t in self.toks)


class Block:
    def __init__(self, toks):
        self.toks = toks

    @property
    def statements(self):
        return [ s for s in self.toks if s.__class__ == Statements ][0]

    def set_statements(self, new_statements):
        if not isinstance(new_statements, Statements):
            new_statements = Statements(new_statements)
        self.toks = [ new_statements if t.__class__ == Statements else t for t in self.toks ]

    def append_set(self, name, value):
        if isinstance(value, bool):
            self.append_toggle(name, value)
            return

        value = ListOfValues.from_list(value) \
            if isinstance(value, list) \
            else Value(value)

        self.statements.append(KeyValuePair(
            [ '\n  ', Key(name), '=', value, ';' ]
        ))

    def append_append(self, name, value):
        if isinstance(value, bool):
            self.append_toggle(name, value)
            return

        value = ListOfValues.from_list(value) \
            if isinstance(value, list) \
            else Value(value)

        self.statements.append(KeyValueAppendPair(
            [ '\n  ', Key(name), '+=', value, ';' ]
        ))

    def append_toggle(self, name, value):
        if not value:
            name = name.split('.')
            name = '.'.join(name[:-1] + [ 'no' + name[-1] ])

        self.statements.append(KeyValueToggle([ '\n  ', Key(name), ';' ]))

    def get(self, name):
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
            _ = self.get(name)
        except KeyError:
            return False
        return True

    def remove_key(self, name):
        if not self.has_key(name):
            raise KeyError
        self.set_statements([ s for s in self.statements \
            if s.__class__ not in [ KeyValuePair, KeyValueAppendPair, KeyValueToggle ] \
            or s.key != name ])

    def __getitem__(self, name):
        if not self.has_key(name):
            raise KeyError
        return self.get(name)

    def __setitem__(self, name, value):
        if self.has_key(name):
            self.remove_key(name)
        self.append_set(name, value)

    def __delitem__(self, name):
        if not self.has_key(name):
            raise KeyError
        self.remove_key(name)

    def __str__(self):
        return ''.join(str(t) for t in self.toks)


class JailBlock(Block):
    @classmethod
    def create(cls, jail_name):
        return cls([ '\n', JailName(jail_name), ' {', Statements(), '\n}' ])

    @property
    def name(self):
        return [ n for n in self.toks if n.__class__ == JailName ][0].value


class JailConf(Block):
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

    def append_jail_block(self, x):
        self.toks.append(x)

    def __getitem__(self, name):
        if self.has_jail_block(name):
            return self.get_jail_block(name)
        return Block.__getitem__(self, name)

    def __setitem__(self, name, value):
        if isinstance(value, JailBlock):
            if self.has_jail_block(name):
                self.remove_jail_block(name)
            self.append_jail_block(value)
        else:
            Block.__setitem__(self, name, value)

    def __delitem__(self, name):
        if self.has_jail_block(name):
            self.remove_jail_block(name)
        else:
            Block.__delitem__(self, name)

    def __str__(self):
        return ''.join(str(t) for t in self.toks)
