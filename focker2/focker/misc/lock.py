import os
import fcntl
from contextlib import ContextDecorator


def focker_lock():
    os.makedirs('/var/lock', exist_ok=True)
    if focker_lock.fd is None:
        focker_lock.fd = open('/var/lock/focker.lock', 'a+')
    print('Waiting for /var/lock/focker.lock ...')
    fcntl.flock(focker_lock.fd, fcntl.LOCK_EX)
    print('Lock acquired.')
focker_lock.fd = None


def focker_unlock():
    if focker_lock.fd is None:
        return
    fcntl.flock(focker_lock.fd, fcntl.LOCK_UN)
    print('Lock released')


class FockerLock(ContextDecorator):
    def __enter__(self):
        focker_lock()

    def __exit__(self, *_):
        focker_unlock()


class FockerUnlock(ContextDecorator):
    def __enter__(self):
        focker_unlock()

    def __exit__(self, *_):
        focker_lock()
