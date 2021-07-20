#
# Copyright (C) 2021, Stanislaw Adaszewski
# See LICENSE for terms
#

from pyparsing import *
from .classes import KeyValuePair, \
    KeyValueAppendPair, \
    KeyValueToggle, \
    JailBlock, \
    JailConf
from .misc import flatten


DEFAULT_WHITE_CHARS = ParserElement.DEFAULT_WHITE_CHARS
ParserElement.setDefaultWhitespaceChars('')


#
# Whitespaces and comments
#

real_sp = Regex('[ \t]*')

not_star = Regex('[^*]')

not_slash = Regex('[^/]')

star_not_slash = Literal("*") + not_slash

multi_line_comment = Literal("/*") + Group(ZeroOrMore(not_star ^ star_not_slash)) + Literal("*/")

not_newlines = Regex('[^\n]*')

single_line_comment = Literal("//") + not_newlines

shell_style_comment = Literal("#") + not_newlines

comment = multi_line_comment ^ single_line_comment ^ shell_style_comment

space_or_newline = Regex('[ \t\n]')

sp = Group(ZeroOrMore(comment ^ space_or_newline))

sp.setParseAction(lambda toks: [ flatten(toks) ])


#
# Strings
#

sing_quote = Literal("'")

dbl_quote = Literal("\"")

esc_sing_quote = Literal("\\'")

esc_dbl_quote = Literal('\\"')

esc_backslash = Literal("\\\\")

sing_quote_safe_char = Regex('[^\'\n\\\\]')

dbl_quote_safe_char = Regex('[^\"\n\\\\]')

continue_line = Literal("\\") + real_sp + Literal("\n")

double_quoted_string = dbl_quote + \
    Group(ZeroOrMore(continue_line ^ esc_dbl_quote ^ esc_backslash ^ dbl_quote_safe_char)) + \
    dbl_quote

single_quoted_string = sing_quote + \
    Group(ZeroOrMore(continue_line ^ esc_sing_quote ^ esc_backslash ^ sing_quote_safe_char)) + \
    sing_quote

quoted_string = single_quoted_string ^ double_quoted_string

unquoted_safe_char = Regex('[^ \t\n;=+\"\',{}]')

unquoted_string = Group(OneOrMore(continue_line ^ unquoted_safe_char))

string = quoted_string ^ unquoted_string

sing_quote.setParseAction(lambda _: [ '' ])
dbl_quote.setParseAction(lambda _: [ '' ])
esc_sing_quote.setParseAction(lambda toks: [ '\'' ])
esc_dbl_quote.setParseAction(lambda toks: [ '"' ])
esc_backslash.setParseAction(lambda toks: [ '\\' ])
continue_line.setParseAction(lambda _: [ '' ])

string.setParseAction(lambda toks: [ flatten(toks) ])


#
# Key-value pairs
#

equal_sign = Literal("=")

plusequal_sign = Literal("+=")

semicolon = Literal(";")

coma = Literal(",")

key = string.copy()

single_value = string.copy()

extra_value = sp + coma + sp + single_value

list_of_values = single_value + Group(OneOrMore(extra_value))

value = list_of_values ^ single_value

key_value_pair = sp + key + sp + equal_sign + sp + value + sp + semicolon

key_value_append_pair = sp + key + sp + plusequal_sign + sp + value + sp + semicolon

key_set = sp + key + sp + semicolon

single_value.addParseAction(lambda toks: [ int(toks[0]) if toks[0].isnumeric() else toks[0] ])
extra_value.setParseAction(lambda toks: [ toks[3] ])
list_of_values.setParseAction(lambda toks: [ [ toks[0] ] + toks[1].asList() ])

key_value_pair.setParseAction(KeyValuePair)
key_value_append_pair.setParseAction(KeyValueAppendPair)
key_set.setParseAction(KeyValueToggle)


#
# Jail blocks
#

curly_open = Literal("{")

curly_close = Literal("}")

jail_name = string

jail_block = sp + jail_name + sp + curly_open + \
    Group(ZeroOrMore(key_value_pair ^ key_value_append_pair ^ key_set)) + \
    sp + curly_close

jail_block.setParseAction(JailBlock)

#
# Top
#

top = Group(ZeroOrMore(key_set ^ key_value_pair ^ key_value_append_pair ^ jail_block)) + \
    sp

top.setParseAction(JailConf)

#
# Actions
#

ParserElement.setDefaultWhitespaceChars(DEFAULT_WHITE_CHARS)
