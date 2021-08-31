#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


import os
from ...misc import focker_unlock
from ...core import focker_subprocess_run, \
    CalledProcessError
from ...core.fenv import substitute_focker_env_vars


def exec_hook(spec, path, fenv, hook_name='exec.prebuild'):
    if isinstance(spec, str):
        spec = [ spec ]
    if not isinstance(spec, list):
        raise TypeError('%s should be a string or a list of strings' % hook_name)
    if not spec:
        return
    spec = ' && '.join(spec)
    spec = substitute_focker_env_vars(spec, fenv)
    print('Running %s command:' % hook_name, spec)
    spec = [ '/bin/sh', '-c', spec ]
    with focker_unlock():
        try:
            res = focker_subprocess_run(spec, cwd=path)
        except CalledProcessError:
            raise RuntimeError('%s failed' % hook_name)


def exec_prebuild(spec, path, fenv):
    return exec_hook(spec, path, fenv, 'exec.prebuild')


def exec_postbuild(spec, path, fenv):
    return exec_hook(spec, path, fenv, 'exec.postbuild')
