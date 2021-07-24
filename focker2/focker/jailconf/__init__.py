from .grammar import top
from .classes import JailConf, \
    JailBlock


class WrapFileOrFilename:
    def __init__(self, file_or_filename, mode='r'):
        self.file_or_filename = file_or_filename
        self.mode = mode
        self.f = None

    def __enter__(self):
        if isinstance(self.file_or_filename, str):
            self.f = open(self.file_or_filename, self.mode)
        else:
            self.f = self.file_or_filename
        return self.f

    def __exit__(self, *exc):
        if isinstance(self.file_or_filename, str):
            self.f.close()
        self.f = None


def loads(s):
    res = top.parseString(s, parseAll=True)
    return res[0]


def load(file_or_filename='/etc/jail.conf'):
    with WrapFileOrFilename(file_or_filename) as f:
        res = top.parseFile(f, parseAll=True)
    return res[0]


def dumps(conf):
    return str(conf)


def dump(conf, file_or_filename='/etc/jail.conf'):
    with WrapFileOrFilename(file_or_filename) as f:
        f.write(str(conf))
