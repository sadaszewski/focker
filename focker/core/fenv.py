import re
from typing import Dict
from .. import yaml
from ..misc import merge_dicts


LINE_CONTINUATION = re.compile(r'\\[ \t\r]*\n')
SUBST_MARKER = re.compile(r'\$\{\{[ \n\t\r]*("(\\"|[^"])*"|\'(\\\'|[^\'])*\'|[a-zA-Z0-9_]*)[ \n\t\r]*\}\}')


class handle_subst_marker:
    def __init__(self, fenv_vars):
        self.fenv_vars = fenv_vars

    def __call__(self, toks):
        # assert len(toks) == 1
        s = toks[0]
        s = LINE_CONTINUATION.sub('', s)
        s = s.encode('utf-8').decode('unicode_escape')
        s = s.strip('${}\n\t\r ')
        if s == '':
            return ''
        elif s.startswith('"') or s.startswith("'"):
            return s[1:-1]
        elif s.lower() in self.fenv_vars:
            return str(self.fenv_vars[s.lower()])
        else:
            raise KeyError(f'FEnv variable not found: {s}')


def substitute_focker_env_vars(s: str, fenv_vars: Dict[str, str]) -> str:
    s = SUBST_MARKER.sub(handle_subst_marker(fenv_vars), s)
    return s


def rec_subst_fenv_vars(o: object, fenv_vars: Dict[str, str]) -> object:
    if isinstance(o, str):
        return substitute_focker_env_vars(o, fenv_vars)
    elif isinstance(o, list) or isinstance(o, tuple):
        return o.__class__( rec_subst_fenv_vars(e, fenv_vars) for e in o )
    elif isinstance(o, dict):
        return o.__class__( ( k, rec_subst_fenv_vars(v, fenv_vars) ) for k, v in o.items() )
    elif isinstance(o, set):
        return o.__class__( rec_subst_fenv_vars(e, fenv_vars) for e in o )
    else:
        return o


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


def fenv_from_list(lst, parent_fenv) -> Dict[str, str]:
    if len(lst) % 2 != 0:
        raise ValueError('List length expected to be divisible by 2')
    fenv = { lst[i].lower(): lst[i + 1] for i in range(0, len(lst), 2) }
    fenv = merge_dicts(fenv, parent_fenv)
    return fenv


def fenv_from_arg(arg, parent_fenv) -> Dict[str, str]:
    if arg is None:
        fenv = dict(parent_fenv)
    elif not isinstance(arg, list):
        raise TypeError('Expected FEnv arg to be a list')
    elif len(arg) == 1:
        fenv = fenv_from_file(arg[0], parent_fenv)
    else:
        fenv = fenv_from_list(arg, parent_fenv)
    return fenv
