#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
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
from ..jailspec import ImageBuildJailSpec
from ..osjail import TemporaryOSJail
from ..fenv import substitute_focker_env_vars
import io


class RunStep(object):
    def __init__(self, spec, src_dir, fenv):
        if isinstance(spec, list):
            spec = [ substitute_focker_env_vars(s, fenv) for s in spec ]
        elif isinstance(spec, str):
            spec = substitute_focker_env_vars(spec, fenv)
        else:
            raise TypeError('Run spec must be a list or a string')

        self.spec = spec
        self.src_dir = src_dir
        self.fenv = fenv

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
            j.run([ '/bin/sh', '-c', spec ])


class CopyStepEntry:
    def __init__(self, spec, src_dir, fenv):
        if not isinstance(spec, list):
            raise TypeError('Copy step specification must be a list')
        if len(spec) < 2 or len(spec) > 3:
            raise ValueError('Copy step specification must have 2 or 3 elements')
        self.spec = spec
        self.src_dir = src_dir
        self.fenv = fenv

        self.src_file = os.path.join(self.src_dir, spec[0])
        self.dst_file = spec[1]
        self.options = spec[2] if len(spec) > 2 else {}
        self.use_fenv = self.options.get('use_fenv', False)

    def hash(self):
        if self.use_fenv:
            with open(self.src_file) as f:
                s = f.read()
                s = substitute_focker_env_vars(s, self.fenv)
                s = s.encode('utf-8')
                return filehash(io.BytesIO(s))
        else:
            return filehash(self.src_file)

    def execute(self, im):
        dst_fnam = os.path.join(im.path, self.dst_file.strip('/'))
        os.makedirs(os.path.split(dst_fnam)[0], exist_ok=True)
        if self.use_fenv:
            with open(self.src_file) as f_1, \
                open(dst_fnam, 'wb') as f_2:
                s = f_1.read()
                s = substitute_focker_env_vars(s, self.fenv)
                s = s.encode('utf-8')
                f_2.write(s)
        else:
            shutil.copyfile(self.src_file, dst_fnam)

        if 'chmod' in self.options:
            os.chmod(dst_fnam, self.options['chmod'])
        if 'chown' in self.options:
            uid, gid = map(int, self.options['chown'].split(':'))
            os.chown(dst_fnam, uid, gid)


class CopyStep(object):
    def __init__(self, spec, src_dir, fenv):
        if not isinstance(spec, list):
            raise TypeError('CopyStep spec should be a list')
        self.spec = spec
        self.src_dir = src_dir
        self.fenv = fenv

        if len(self.spec) == 0:
            self.entries = []
        elif isinstance(self.spec[0], list):
            self.entries = [ CopyStepEntry(e, src_dir, fenv) for e in self.spec ]
        else:
            self.entries = [ CopyStepEntry(self.spec, src_dir, fenv) ]

    def hash(self, base, **kwargs):
        fh = [ e.hash() for e in self.entries ]
        res = hashlib.sha256(
            json.dumps(( base, fh, self.spec ))
            .encode('utf-8')).hexdigest()
        return res

    def execute(self, im, **kwargs):
        for e in self.entries:
            e.execute(im)


def create_step(spec, src_dir, fenv):
    if not isinstance(spec, dict):
        raise TypeError(f'Step specification must be a dictionary, got: {spec.__class__.__name__} ({spec})')
    if 'copy' in spec:
        return CopyStep(spec['copy'], src_dir=src_dir, fenv=fenv)
    elif 'run' in spec:
        return RunStep(spec['run'], src_dir=src_dir, fenv=fenv)
    raise ValueError('Unrecognized step spec: ' + json.dumps(spec))
