from contextvars import ContextVar
from .process import focker_subprocess_check_output
from .zfs import zfs_properties_cache
from typing import List


# JAILS_CACHE = ContextVar('JAILS_CACHE')
# DATASET_CACHE = ContextVar('DATASET_CACHE')


class CacheBase:
    context_var = None

    def __init__(self):
        self.tok = None

    def __enter__(self):
        self.tok = self.context_var.set(self)
        self.generate_cache()

    def __exit__(self, *excinfo):
        self.context_var.reset(self.tok)
        self.tok = None

    def generate_cache(self):
        raise NotImplementedError

    @classmethod
    def available(self):
        return ( self.context_var.get() is not None )

    @classmethod
    def get_property(cls, *args):
        if cls.context_var.get() is None:
            raise RuntimeError('No cache in the current context')
        return cls.context_var.get()._get_property(*args)

    def _get_property(self, *args):
        raise NotImplementedError


class JailsCache:
    def __init__(self):
        self.tok = None

    def __enter__(self):
        self.tok = JAILS_CACHE.set(self)

    def __exit__(self):
        JAILS_CACHE.reset(self.tok)
        self.tok = None


class DatasetCache(CacheBase):
    context_var = ContextVar('DATASET_CACHE', None)

    def __init__(self, focker_type: List[str]):
        super().__init__()
        self.focker_type = focker_type
        self.data = {}

    def generate_cache(self):
        for ft in self.focker_type:
            self.data.update(zfs_properties_cache(ft))

    def _get_property(self, name, propname):
        return self.data.get(( name, propname ), '-')
