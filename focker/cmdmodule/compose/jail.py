#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from ...core import clone_image_jailspec, \
    OSJailSpec, \
    JailFs, \
    OSJail
from ...core.fenv import rec_subst_fenv_vars


def build_jails(spec, fenv):
    print('Removing existing jails...')
    for tag, _ in spec.items():
        # tag = substitute_focker_env_vars(tag, fenv)
        jfs = JailFs.from_tag(tag, raise_exc=False)
        if jfs is not None:
            jfs.destroy()

    print('Building new jails...')
    for tag, jspec in spec.items():
        # tag = substitute_focker_env_vars(tag, fenv)
        jspec = rec_subst_fenv_vars(jspec, fenv)
        jspec['name'] = jspec.get('name', tag)
        with clone_image_jailspec(jspec) as (jspec, _, jfs_take_ownership):
            jfs = jfs_take_ownership()
            jfs.add_tags([ tag ])
            ospec = OSJailSpec.from_jailspec(jspec)
            ospec.add()
