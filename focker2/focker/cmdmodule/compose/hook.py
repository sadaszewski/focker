import os
from ...misc import FockerUnlock


def exec_hook(spec, path, hook_name='exec.prebuild'):
    if isinstance(spec, str):
        spec = [ spec ]
    if not isinstance(spec, list):
        raise ValueError('%s should be a string or a list of strings' % hook_name)
    if not spec:
        return
    spec = ' && '.join(spec)
    print('Running %s command:' % hook_name, spec)
    spec = [ '/bin/sh', '-c', spec ]
    oldwd = os.getcwd()
    os.chdir(path)
    with FockerUnlock():
        res = focker_subprocess_run(spec)
    if res.returncode != 0:
        raise RuntimeError('%s failed' % hook_name)
    os.chdir(oldwd)


def exec_prebuild(spec, path):
    return exec_hook(spec, path, 'exec.prebuild')


def exec_postbuild(spec, path):
    return exec_hook(spec, path, 'exec.postbuild')
