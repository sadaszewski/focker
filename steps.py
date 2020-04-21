import hashlib
import json


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
    def __init__(self, base, spec):
        self.base = base
        self.spec = spec

    def hash(self):
        res = hashlib.sha256(
            json.dumps(( self.base, self.spec ))
            .encode('utf-8')).hexdigest()
        return res


class CopyStep(object):
    def __init__(self, base, spec):
        if not isinstance(spec, list):
            raise ValueError('CopyStep spec should be a list')
        self.base = base
        self.spec = spec

    def hash(self):
        if len(self.spec) == 0:
            fh = []
        elif isinstance(self.spec[0], list):
            fh = list(map(lambda a: filehash(a[0]), self.spec))
        else:
            fh = [ filehash(self.spec[0]) ]
        res = hashlib.sha256(
            json.dumps(( self.base, fh, self.spec ))
            .encode('utf-8')).hexdigest()
        return res
