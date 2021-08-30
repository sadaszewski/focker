import re
from typing import Dict
from .. import yaml
from ..misc import merge_dicts


LINE_CONTINUATION = re.compile(r'\\[ \t\r]*\n')
SUBST_MARKER = re.compile(r'\{\{[ \n\t\r]*("(\\"|[^"])*"|\'(\\\'|[^\'])*\'|[a-zA-Z0-9_]*)[ \n\t\r]*\}\}')


class handle_subst_marker:
    def __init__(self, fenv_vars):
        self.fenv_vars = fenv_vars

    def __call__(self, toks):
        # assert len(toks) == 1
        s = toks[0]
        s = LINE_CONTINUATION.sub('', s)
        s = s.encode('utf-8').decode('unicode_escape')
        s = s.strip('{}\n\t\r ')
        if s == '':
            return ''
        elif s.startswith('"') or s.startswith("'"):
            return s[1:-1]
        elif s.lower() in self.fenv_vars:
            return self.fenv_vars[s.lower()]
        else:
            raise KeyError(f'FEnv variable not found: {s}')


def substitute_focker_env_vars(s: str, fenv_vars: Dict[str, str]) -> str:
    s = SUBST_MARKER.sub(handle_subst_marker(fenv_vars), s)
    return s


def lower_keys(d: Dict) -> Dict:
    return { k.lower(): v for k, v in d.items() }


def fenv_from_spec(spec: Dict, parent_fenv) -> Dict[str, str]:
    if 'fenv' in spec:
        fenv = lower_keys(spec['fenv'])
    else:
        fenv = {}
    return merge_dicts(fenv, parent_fenv)


def fenv_from_file(fname: str, parent_fenv) -> Dict[str, str]:
    with open(fname, 'r') as f:
        fenv = yaml.safe_load(f)
        fenv = lower_keys(fenv)
    return merge_dicts(fenv, parent_fenv)
