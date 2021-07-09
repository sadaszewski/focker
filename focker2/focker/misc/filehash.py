import hashlib


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
