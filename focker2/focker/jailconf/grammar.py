#
# Copyright (C) 2021, Stanislaw Adaszewski
# See LICENSE for terms
#

import parsimonious

GRAMMAR = parsimonious.Grammar(r"""

top = (key_set / key_value_pair / key_value_append_pair / jail_block)* sp

jail_block = sp jail_name sp curly_open (key_value_pair / key_value_append_pair / key_set)* sp curly_close

curly_open = "{"

curly_close = "}"

jail_name = string

key_value_pair = sp key sp equal_sign sp value sp semicolon

key_value_append_pair = sp key sp plusequal_sign sp value sp semicolon

key_set = sp key sp semicolon

equal_sign = "="

plusequal_sign = "+="

semicolon = ";"

key = string

value = list_of_values / single_value

single_value = string

list_of_values = single_value (sp coma sp single_value)+

coma = ","

string = quoted_string / unquoted_string

unquoted_string = (continue_line / unquoted_safe_char)+

unquoted_safe_char = ~'[^ \t\n;=+\"\',{}]'

continue_line = "\\" real_sp "\n"

quoted_string = single_quoted_string / double_quoted_string

single_quoted_string = sing_quote (continue_line / esc_sing_quote / esc_backslash / sing_quote_safe_char)* sing_quote

double_quoted_string = dbl_quote (continue_line / esc_dbl_quote / esc_backslash / dbl_quote_safe_char)* dbl_quote

sing_quote = "'"

dbl_quote = "\""

esc_sing_quote = "\\'"

esc_dbl_quote = '\\"'

esc_backslash = "\\\\"

sing_quote_safe_char = ~'[^\'\n\\\\]'

dbl_quote_safe_char = ~'[^\"\n\\\\]'

comment = multi_line_comment / single_line_comment / shell_style_comment

single_line_comment = "//" not_newlines

not_newlines = ~'[^\n]*'

multi_line_comment = "/*" (not_star / star_not_slash)* "*/"

not_star = ~'[^*]'

not_slash = ~'[^/]'

star_not_slash = "*" not_slash

shell_style_comment = "#" ~'[^\n]*'

sp = ( comment / " " / "\t" / "\n")*

real_sp = (" " / "\t" )*

""")
