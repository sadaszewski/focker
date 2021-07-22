from pyparsing import *
from .classes import *
from functools import reduce
import re


#
# Customize ParserElement
#

DEFAULT_WHITE_CHARS = ParserElement.DEFAULT_WHITE_CHARS
ParserElement.setDefaultWhitespaceChars('')
ParserElement.enablePackrat()


#
# Tokens
#

OPEN_BRACE = Literal('{')
CLOSE_BRACE = Literal('}')
EQUAL = Literal('=')
COMMA = Literal(',')
PLUS_EQUAL = Literal('+=')
SEMICOLON = Literal(';')

C_STYLE_COMMENT = Regex(r'/\*((?!\*/).|\n)*\*/')
CPP_STYLE_COMMENT = Regex(r'//.*')
SHELL_STYLE_COMMENT = Regex(r'\#.*')
LINE_CONTINUATION = Regex(r'\\[ \t\r]*\n')
UNQUOTED_STRING = Regex(r'(\\[ \t\r]*\n|[^\"\'{}=,+; \t\r\n\\])+')
DOUBLE_QUOTED_STRING = Regex(r'"(\\"|[^"])*"')
SINGLE_QUOTED_STRING = Regex(r"'(\\'|[^'])*'")
SPACE = Regex(r'[ \t\n\r]*')


DOUBLE_QUOTED_STRING.setParseAction(lambda toks: toks[0][1:-1])
SINGLE_QUOTED_STRING.setParseAction(lambda toks: toks[0][1:-1])


# Helpers

comment = C_STYLE_COMMENT | CPP_STYLE_COMMENT | SHELL_STYLE_COMMENT
sp = SPACE | comment
string = UNQUOTED_STRING | DOUBLE_QUOTED_STRING | SINGLE_QUOTED_STRING

def proc_str(toks):
    assert len(toks) == 1
    s = toks[0]
    s = LINE_CONTINUATION.re.sub('', s)
    s = s.encode('utf-8').decode('unicode_escape')
    return s

string.setParseAction(proc_str)

#
# Key-value pairs
#

key = string.copy()
single_value = string.copy()
extra_value = sp + COMMA + sp + single_value
list_of_values = single_value + Group(OneOrMore(extra_value))
value = list_of_values | single_value
key_value_pair = sp + key + sp + EQUAL + sp + value + sp + SEMICOLON
key_value_append_pair = sp + key + sp + PLUS_EQUAL + sp + value + sp + SEMICOLON
key_set = sp + key + sp + SEMICOLON

key.addParseAction(Key)
single_value.addParseAction(Value)
list_of_values.setParseAction(ListOfValues)
key_value_pair.setParseAction(KeyValuePair)
key_value_append_pair.setParseAction(KeyValueAppendPair)
key_set.setParseAction(KeyValueToggle)


#
# Jail blocks
#

statements = Group(ZeroOrMore(key_value_pair | key_value_append_pair | key_set))

jail_name = string.copy()
jail_block = sp + jail_name + sp + OPEN_BRACE + statements + sp + CLOSE_BRACE

statements.setParseAction(Statements)
jail_block.setParseAction(JailBlock)


#
# Top
#

top = Group(ZeroOrMore(key_set | key_value_pair | key_value_append_pair | jail_block)) + \
    sp

top.setParseAction(JailConf)


#
# Restore ParserElement settings
#

ParserElement.setDefaultWhitespaceChars(DEFAULT_WHITE_CHARS)
