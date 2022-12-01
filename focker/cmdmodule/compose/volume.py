#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from ...core import Volume
import os
from ...core.fenv import rec_subst_fenv_vars


def build_volumes(spec, fenv):
    for tag, params in spec.items():
        # tag = substitute_focker_env_vars(tag, fenv)
        if Volume.exists_tag(tag):
            v = Volume.from_tag(tag)
        else:
            v = Volume.create()
            v.add_tags([ tag ])
        params = rec_subst_fenv_vars(params, fenv)
        print('params:', params)
        if 'chown' in params:
            os.chown(v.path, *map(int, params['chown'].split(':')))
        if 'chmod' in params:
            mode = params['chmod']
            if isinstance(mode, str):
                mode = int(mode, 0)
            os.chmod(v.path, mode)
        if 'zfs' in params:
            v.set_props(params['zfs'])
        if 'protect' in params:
            if params['protect']:
                v.protect()
            else:
                v.unprotect()
