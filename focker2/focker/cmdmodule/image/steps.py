#
# Copyright (C) Stanislaw Adaszewski, 2020
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#

import hashlib
import json
import shutil
import os
import shlex
from ...misc import filehash
from ...core import ImageBuildJailSpec, \
    TemporaryOSJail


class RunStep(object):
    def __init__(self, spec, src_dir):
        if not isinstance(spec, list) and \
            not isinstance(spec, str):
            raise ValueError('Run spec must be a list or a string')
        self.spec = spec
        self.src_dir = src_dir

    def hash(self, base, **kwargs):
        res = hashlib.sha256(
            json.dumps(( base, self.spec ))
            .encode('utf-8')).hexdigest()
        return res

    def execute(self, im, **kwargs):
        spec = self.spec
        if isinstance(spec, list):
            spec = ' && ' .join(self.spec)
        jspec = ImageBuildJailSpec.from_image_and_dict(im, {})
        with TemporaryOSJail(jspec) as j:
            j.run(spec)


class CopyStep(object):
    def __init__(self, spec, src_dir):
        if not isinstance(spec, list):
            raise ValueError('CopyStep spec should be a list')
        self.spec = spec
        self.src_dir = src_dir

    def hash(self, base, args, **kwargs):
        if len(self.spec) == 0:
            fh = []
        elif isinstance(self.spec[0], list):
            fh = list(map(lambda a: filehash(os.path.join(self.src_dir, a[0])), self.spec))
        else:
            fh = [ filehash(os.path.join(self.src_dir, self.spec[0])) ]
        res = hashlib.sha256(
            json.dumps(( base, fh, self.spec ))
            .encode('utf-8')).hexdigest()
        return res

    def execute(self, im, args, **kwargs):
        lst = [ self.spec ] \
            if not isinstance(self.spec[0], list) \
            else self.spec
        for entry in lst:
            (source, target) = entry[:2]
            options = entry[2] if len(entry) > 2 else {}
            target = target.strip('/')
            os.makedirs(os.path.split(os.path.join(im.path, target))[0], exist_ok=True)
            shutil.copyfile(os.path.join(self.src_dir, source),
                os.path.join(im.path, target))
            if 'chmod' in options:
                os.chmod(os.path.join(im.path, target), options['chmod'])
            if 'chown' in options:
                uid, gid = map(int, options['chown'].split(':'))
                os.chown(os.path.join(im.path, target), uid, gid)


def create_step(spec, src_dir):
    if not isinstance(spec, dict):
        raise ValueError('Step specification must be a dictionary')
    if 'copy' in spec:
        return CopyStep(spec['copy'], src_dir=src_dir)
    elif 'run' in spec:
        return RunStep(spec['run'], src_dir=src_dir)
    raise ValueError('Unrecognized step spec: ' + json.dumps(spec))
