import hashlib
import json
from jail import jail_run
import shutil


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

    def hash(self, base):
        res = hashlib.sha256(
            json.dumps(( base, self.spec ))
            .encode('utf-8')).hexdigest()
        return res

    def execute(self, path):
        spec = self.spec
        if isinstance(spec, list)
            spec = ' && ' .join(self.spec)
        jail_run(path, spec)


class CopyStep(object):
    def __init__(self, spec):
        if not isinstance(spec, list):
            raise ValueError('CopyStep spec should be a list')
        self.spec = spec

    def hash(self, base):
        if len(self.spec) == 0:
            fh = []
        elif isinstance(self.spec[0], list):
            fh = list(map(lambda a: filehash(a[0]), self.spec))
        else:
            fh = [ filehash(self.spec[0]) ]
        res = hashlib.sha256(
            json.dumps(( base, fh, self.spec ))
            .encode('utf-8')).hexdigest()
        return res

    def execute(self, path):
        lst = [ self.spec ] \
            if not isinstance(self.spec[0], list) \
            else self.spec
        for a in lst:
            shutil.copyfile(a[0], os.path.join(path, a[1]))


def create_step(spec):
    if not isinstance(spec, dict):
        raise ValueError('Step specification must be a dictionary')
    if 'copy' in spec:
        return CopyStep(spec['copy'])
    elif 'run' in spec:
        return RunStep(spec['run'])
    raise ValueError('Unrecognized step spec: ' + json.dumps(spec))
