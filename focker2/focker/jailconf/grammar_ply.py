from ply import lex, \
    yacc
import re
from .classes import *


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


class Parser(object):

    def p_conf(self, p):
        " conf : global_scope "
        p[0] = p[1]

    def p_space_or_comment(self, p):
        """ space_or_comment : space_or_comment SPACE
            space_or_comment : space_or_comment SHELL_STYLE_COMMENT
            space_or_comment : space_or_comment C_STYLE_COMMENT
            space_or_comment : space_or_comment CPP_STYLE_COMMENT """
        p[0] = p[1] + p[2]

    def p_space_or_comment_empty(self, p):
        " space_or_comment : "
        p[0] = ''

    def p_global_scope_1(self, p):
        """ global_scope : global_scope statement
            global_scope : global_scope jail_definition """
        print('p_global_scope_1:', list(p))
        p[0] = p[1]
        p[0].add_statement(p[2])

    def p_global_scope_space(self, p):
        " global_scope : global_scope space_or_comment"
        p[0] = p[1]
        p[0].add_statement(p[2])

    def p_global_scope_empty(self, p):
        " global_scope : "
        p[0] = JailConf.create()

    def p_jail_block(self, p):
        " jail_definition : space_or_comment value space_or_comment OPEN_BRACE statement_list space_or_comment CLOSE_BRACE "
        print('p_jail_block:', list(p))
        p[0] = JailBlock(p[1:])

    def p_statement_list(self, p):
        " statement_list : statement_list statement "
        print('statement_list:', list(p))
        p[0] = p[1] + [ p[2] ]

    def p_statement_list_empty(self, p):
        " statement_list : "
        p[0] = []

    def p_statement(self, p):
        """ statement : affectation
            statement : declaration
            statement : append """
        p[0] = p[1]

    def p_affectation(self, p):
        """ affectation : space_or_comment parameter space_or_comment EQUAL space_or_comment value space_or_comment SEMICOLON
            affectation : space_or_comment parameter space_or_comment EQUAL space_or_comment many_values space_or_comment SEMICOLON """
        print('affectation:', list(p))
        p[0] = KeyValuePair(p[1:])

    def p_append(self, p):
        """ append : space_or_comment parameter space_or_comment PLUS_EQUAL space_or_comment value space_or_comment SEMICOLON
            append : space_or_comment parameter space_or_comment PLUS_EQUAL space_or_comment many_values space_or_comment SEMICOLON """
        p[0] = KeyValueAppendPair(p[1:])

    def p_declaration(self, p):
        " declaration : space_or_comment parameter space_or_comment SEMICOLON "
        p[0] = KeyValueToggle (p[1:])

    def p_parameter(self, p):
        " parameter : NAME "
        p[0] = p[1]

    def p_single_quoted_string(self, p):
        " single_quoted_string : SINGLE_QUOTED_STRING "
        s = p[1][1:-1]
        s = s.replace('\\\\', '\\')
        s = s.replace('\\\'', '\'')
        p[0] = s

    def p_double_quoted_string(self, p):
        " double_quoted_string : DOUBLE_QUOTED_STRING "
        s = p[1][1:-1]
        s = s.replace('\\\\', '\\')
        s = s.replace('\\"', '"')
        p[0] = s

    def p_value(self, p):
        """ value : NAME
            value : single_quoted_string
            value : double_quoted_string """
        p[0] = p[1]

    def p_many_values(self, p):
        " many_values : space_or_comment many_values space_or_comment COMMA space_or_comment value "
        p[0] = p[2]
        p[0].append(p[6])

    def p_many_values_only_two(self, p):
        " many_values : space_or_comment value space_or_comment COMMA space_or_comment value "
        p[0] = [p[1], p[3]]

    def p_error(self, p):
        raise RuntimeError(repr(p))

    def __init__(self, lexer = None):
        lexer = lexer or Lexer()
        self.tokens = lexer.tokens
        self._lexer = lexer
        self._parser = yacc.yacc(module=self, debug=True, write_tables=0)

    def parse(self, entry):
        return self._parser.parse(entry, lexer = self._lexer.lexer)
