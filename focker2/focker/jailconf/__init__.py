from .grammar import top
from .classes import JailConf, \
    JailBlock


def loads(s):
    res = top.parseString(s, parseAll=True)
    return res[0]


def load(file):
    res = top.parseFile(file, parseAll=True)
    return res[0]


def dumps(conf):
    return str(conf)


def dump(conf, file):
    with open(file_or_filename) as f:
        f.write(str(conf))
