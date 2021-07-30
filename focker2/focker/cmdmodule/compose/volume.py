from ...core import Volume
import os


def build_volumes(spec):
    for tag, params in spec.items():
        if Volume.exists_tag(tag):
            v = Volume.from_tag(tag)
        else:
            v = Volume.create()
            v.add_tags([ tag ])
        print('params:', params)
        if 'chown' in params:
            os.chown(v.path, *map(int, params['chown'].split(':')))
        if 'chmod' in params:
            os.chmod(v.path, params['chmod'])
        if 'zfs' in params:
            v.set_props(params['zfs'])
        if 'protect' in params:
            if params['protect']:
                v.protect()
            else:
                v.unprotect()
