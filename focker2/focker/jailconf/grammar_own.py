class Lexer:
    tokens = (
        'OPEN_BRACE',
        'CLOSE_BRACE',
        'EQUAL',
        'COMMA',
        'PLUS_EQUAL',
        'SEMICOLON',
        'NAME',
        'DOUBLE_QUOTED_STRING',
        'SINGLE_QUOTED_STRING',
        'SPACE',
        'SHELL_STYLE_COMMENT',
        'C_STYLE_COMMENT',
        'CPP_STYLE_COMMENT'
    )

    t_OPEN_BRACE = '{'
    t_CLOSE_BRACE = '}'
    t_EQUAL = '='
    t_COMMA = ','
    t_PLUS_EQUAL = r'\+='
    t_SEMICOLON = ';'

    def t_C_STYLE_COMMENT(self, token):
        r'/\*((?!\*/).|\n)*\*/'
        return token

    def t_CPP_STYLE_COMMENT(self, token):
        r'//.*'
        return token

    def t_SHELL_STYLE_COMMENT(self, token):
        r'\#.*'
        return token

    def t_NAME(self, token):
        r'\$?[-a-zA-Z0-9._/*:]+'
        return token

    def t_DOUBLE_QUOTED_STRING(self, token):
        r'"(\\\\|\\"|[^"\\])*"'
        return token

    def t_SINGLE_QUOTED_STRING(self, token):
        r"'(\\\\|\\'|[^'\\])*'"
        return token

    t_SPACE = r'[ \r\n\t]+'

    def t_error(self, token):
        raise RuntimeError(
            "Illegal character '%s', line %s" % (
                token.value[0],
                token.lineno
            )
        )

    def __init__(self):
        self.lexer = lex.lex(object=self, debug=0, reflags = re.MULTILINE)


class Parser:
    def __init__(self):
        patterns = dict(
            assignment=['NAME', 'EQUAL', '']
        )

    def parse(self, text):
        lexer = Lexer()
        lexer.input(text)
        state = []
        while True:
            tok = lexer.token()
            state.append(tok)
