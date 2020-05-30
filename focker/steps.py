#
# Copyright (C) Stanislaw Adaszewski, 2020
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#

import hashlib
import json
from .jail import jail_run
import shutil
import os
import shlex
from .misc import filehash


class RunStep(object):
    def __init__(self, spec):
        if not isinstance(spec, list) and \
            not isinstance(spec, str):
            raise ValueError('Run spec must be a list or a string')
        self.spec = spec

    def hash(self, base, **kwargs):
        res = hashlib.sha256(
            json.dumps(( base, self.spec ))
            .encode('utf-8')).hexdigest()
        return res

    def execute(self, path, **kwargs):
        spec = self.spec
        if isinstance(spec, list):
            spec = ' && ' .join(self.spec)
        jail_run(path, spec)


class CopyStep(object):
    def __init__(self, spec):
        if not isinstance(spec, list):
            raise ValueError('CopyStep spec should be a list')
        self.spec = spec

    def hash(self, base, args, **kwargs):
        if len(self.spec) == 0:
            fh = []
        elif isinstance(self.spec[0], list):
            fh = list(map(lambda a: filehash(os.path.join(args.focker_dir, a[0])), self.spec))
        else:
            fh = [ filehash(os.path.join(args.focker_dir, self.spec[0])) ]
        res = hashlib.sha256(
            json.dumps(( base, fh, self.spec ))
            .encode('utf-8')).hexdigest()
        return res

    def execute(self, path, **kwargs):
        lst = [ self.spec ] \
            if not isinstance(self.spec[0], list) \
            else self.spec
        for entry in lst:
            (source, target) = entry[:2]
            options = entry[2] if len(entry) > 2 else {}
            target = target.strip('/')
            os.makedirs(os.path.split(os.path.join(path, target))[0], exist_ok=True)
            shutil.copyfile(os.path.join(kwargs['args'].focker_dir, source),
                os.path.join(path, target))
            if 'chmod' in options:
                os.chmod(os.path.join(path, target), options['chmod'])
            if 'chown' in options:
                uid, gid = options['chown'].split(':').map(int)
                os.chown(os.path.join(path, target), uid, gid)


def create_step(spec):
    if not isinstance(spec, dict):
        raise ValueError('Step specification must be a dictionary')
    if 'copy' in spec:
        return CopyStep(spec['copy'])
    elif 'run' in spec:
        return RunStep(spec['run'])
    raise ValueError('Unrecognized step spec: ' + json.dumps(spec))
