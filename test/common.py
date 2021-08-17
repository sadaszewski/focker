import os


def _read_file_if_exists(fname, default=None):
    if os.path.exists(fname):
        with open(fname, 'r') as f:
            return f.read()

    return default
