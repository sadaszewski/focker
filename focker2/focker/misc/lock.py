import os
import fcntl
from contextlib import ContextDecorator


class focker_lock(ContextDecorator):
    fd = None

    def __enter__(self):
        os.makedirs('/var/lock', exist_ok=True)
        if focker_lock.fd is not None:
            raise RuntimeError('focker_lock.fd expected to be None here')
        focker_lock.fd = open('/var/lock/focker.lock', 'a+')
        print('Waiting for /var/lock/focker.lock ...')
        fcntl.flock(focker_lock.fd, fcntl.LOCK_EX)
        print('Lock acquired.')

    def __exit__(self, *_):
        fcntl.flock(focker_lock.fd, fcntl.LOCK_UN)
        print('Lock released')
        focker_lock.fd.close()
        focker_lock.fd = None


class focker_unlock(ContextDecorator):
    def __enter__(self):
        if focker_lock.fd is None:
            return
        fcntl.flock(focker_lock.fd, fcntl.LOCK_UN)
        print('Lock released temporarily')

    def __exit__(self, *_):
        if focker_lock.fd is None:
            return
        print('Waiting for /var/lock/focker.lock ...')
        fcntl.flock(focker_lock.fd, fcntl.LOCK_EX)
        print('Lock reclaimed.')
