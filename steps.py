import hashlib
import json
from .jail import jail_run
import shutil
import os
import shlex


def filehash(fname):
    h = hashlib.sha256()
    with open(fname, 'rb') as f:
        while True:
            data = f.read(1024*1024*4)
            if not data:
                break
            h.update(data)
    res = h.hexdigest()
    return res


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
        for a in lst:
            source, target = a
            if target.startswith('/'):
                target = target[1:]
            shutil.copyfile(os.path.join(kwargs['args'].focker_dir, source),
                os.path.join(path, target))


def create_step(spec):
    if not isinstance(spec, dict):
        raise ValueError('Step specification must be a dictionary')
    if 'copy' in spec:
        return CopyStep(spec['copy'])
    elif 'run' in spec:
        return RunStep(spec['run'])
    raise ValueError('Unrecognized step spec: ' + json.dumps(spec))
