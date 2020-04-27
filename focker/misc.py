import random
from .zfs import zfs_exists


def random_sha256_hexdigest():
    return bytes([ random.randint(0, 255) for _ in range(32) ]).hex()


def find_prefix(head, tail):
    for pre in range(7, len(tail)):
        name = head + tail[:pre]
        if not zfs_exists(name):
            break
    return name
