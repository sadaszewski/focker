#
# Copyright (C) Stanislaw Adaszewski, 2020-2021
# License: GNU General Public License v3.0
# URL: https://github.com/sadaszewski/focker
# URL: https://adared.ch/focker
#


from .zfs import *


#def property(fn):
#    def inner(self):
#        if hasattr(self.property_cache) and self.property_cache is not None and \
#            fn.__name__ in self.property_cache:
#            return self.property_cache[fn.__name__]
#        else:
#            return fn(self)
#    return inner


Dataset = 'Dataset'

class Dataset:
    _meta_class = None
    _meta_list_columns = ['name', 'mountpoint', 'focker:sha256', 'focker:tags', 'rdonly', 'used']
    _meta_focker_type = 'image'
    _meta_zfs_type = 'filesystem'
    _meta_cloneable_from = None
    _meta_can_finalize = True
    _init_key = object()

    def __init__(self, **kwargs):
        if 'init_key' not in kwargs or kwargs['init_key'] != self._init_key:
            raise RuntimeError(f'{self.__class__.__name__} must be created using one of the factory methods')

        self.name = kwargs['name']
        self.sha256 = kwargs['sha256']
        self.mountpoint = kwargs['mountpoint']
        self.property_cache = kwargs.get('property_cache')

    @classmethod
    def from_name(cls, name):
        sha256 = zfs_get_property(name, 'focker:sha256')
        mountpoint = zfs_mountpoint(name)
        return cls(init_key=cls._init_key, name=name, sha256=sha256, mountpoint=mountpoint)

    @classmethod
    def clone_from(cls, base: Dataset, sha256: str = None) -> Dataset:
        if cls._meta_cloneable_from is None:
            raise RuntimeError(f'{cls.__name__} cannot be created by cloning')
        if not isinstance(base, cls._meta_cloneable_from):
            raise TypeError(f'{base.__class__.__name__} is not the expected type - {cls._meta_cloneable_from.__name__}')
        if not base.is_finalized:
            raise RuntimeError(f'{base.__class__.__name__} must be finalized')
        if sha256 is None:
            sha256 = random_sha256_hexdigest()
        if zfs_exists_props({ 'focker:sha256': sha256 }, focker_type=cls._meta_focker_type,
            zfs_type=cls._meta_zfs_type):
            raise RuntimeError(f'{cls.__name__} with specified SHA256 already exists')
        name = zfs_shortest_unique_name(sha256, focker_type=cls._meta_focker_type)
        zfs_clone(base.snapshot_name, name, { 'focker:sha256': sha256 })
        mountpoint = zfs_mountpoint(name)
        return cls._meta_class(init_key=cls._init_key, name=name, sha256=sha256,
            mountpoint=mountpoint)

    def finalize(self):
        if not self._meta_can_finalize:
            raise RuntimeError(f'{self.__class__.__name__} cannot be finalized')
        zfs_set_props(self.name, { 'rdonly': 'on' })
        zfs_snapshot(self.snapshot_name)

    @property
    def is_finalized(self):
        res = self.get_property('rdonly')
        return (res == 'on')

    @property
    def tags(self):
        res = self.get_property('focker:tags')
        res = res.split(' ')
        res = [ t for t in res if t != '-' ]
        return set(res)

    @property
    def snapshot_name(self):
        return self.name + '@1'

    @property
    def size(self):
        return self.get_property('used')

    @classmethod
    def list(cls):
        res = zfs_list(cls._meta_list_columns, focker_type=cls._meta_focker_type,
            zfs_type=cls._meta_zfs_type)
        res = [ cls._meta_class(init_key=cls._init_key, name=name, sha256=sha256,
            mountpoint=mountpoint)
                for name, mountpoint, sha256, *_ in res ]
        return res

    @classmethod
    def from_predicate_handle_corner_cases(cls, lst, raise_exc=True):
        if len(lst) == 0:
            if raise_exc:
                raise RuntimeError(f'{cls.__name__} not found')
            else:
                return None
        if len(lst) > 1:
            if raise_exc:
                raise RuntimeError(f'Ambiguous {cls.__name__.lower()} reference')
            else:
                return None
        return lst

    @classmethod
    def exists_predicate(cls, pred):
        lst = zfs_list(cls._meta_list_columns,
            focker_type=cls._meta_focker_type, zfs_type=cls._meta_zfs_type)
        lst = [ e for e in lst if pred(e) ]
        if len(lst) == 0:
            return False
        elif len(lst) == 1:
            return True
        else:
            raise RuntimeError('Ambiguous reference')

    @classmethod
    def exists_sha256(cls, sha256: str):
        return cls.exists_predicate(lambda e: e[2] == sha256)

    @classmethod
    def exists_tag(cls, tag: str):
        return cls.exists_predicate(lambda e: tag in e[3].split(' '))

    @classmethod
    def from_predicate(cls, pred, raise_exc=True):
        lst = zfs_list(cls._meta_list_columns,
            focker_type=cls._meta_focker_type, zfs_type=cls._meta_zfs_type)
        lst = [ e for e in lst if pred(e) ]
        # print(lst)
        lst = cls.from_predicate_handle_corner_cases(lst, raise_exc=raise_exc)
        if lst is None:
            return None
        name, mountpoint, sha256, *_ = lst[0]
        return cls._meta_class(init_key=cls._init_key, name=name, sha256=sha256,
            mountpoint=mountpoint)

    @classmethod
    def from_sha256(cls, sha256: str):
        return cls.from_predicate(lambda e: e[2] == sha256)

    @classmethod
    def from_tag(cls, tag: str, raise_exc=True):
        return cls.from_predicate(lambda e: tag in e[3].split(' '), raise_exc=raise_exc)

    @classmethod
    def from_partial_sha256(cls, sha256: str):
        return cls.from_predicate(lambda e: e[2].startswith(sha256))

    @classmethod
    def from_partial_tag(cls, tag: str):
        return cls.from_predicate(lambda e: any(t.startswith(tag) for t in e[3].split(' ')))

    @classmethod
    def from_any_id(cls, id_: str, strict=True, raise_exc=True):
        if strict:
            return cls.from_predicate(lambda e: \
                id_ in e[3].split(' ') or e[2] == id_, raise_exc=raise_exc)
        else:
            return cls.from_predicate(lambda e: \
                any(t.startswith(id_) for t in e[3].split(' ')) or \
                e[2].startswith(id_), raise_exc=raise_exc)

    def add_tags(self, tags):
        if tags is None:
            return
        zfs_untag(tags, focker_type=self._meta_focker_type)
        zfs_tag(self.name, tags)

    def remove_tags(self, tags):
        if tags is None:
            return
        if any(t not in self.tags for t in tags):
            raise RuntimeError(f'This {self.__class__.__name__.lower()} does not seem to be tagged with all the specified tags')
        zfs_untag(tags, focker_type=self._meta_focker_type)

    @classmethod
    def untag(cls, tags):
        zfs_untag(tags, focker_type=cls._meta_focker_type)

    def in_use(self):
        if not zfs_exists(self.name):
            return False
        lst = [ ds for ds in self.list_unused() \
            if ds.name == self.name ]
        return ( len(lst) == 0 )

    @classmethod
    def list_unused(cls):
        raise NotImplementedError # pragma: no cover

    @classmethod
    def create(cls, sha256=None):
        if sha256 is None:
            sha256 = random_sha256_hexdigest()
        if cls.exists_sha256(sha256):
            raise RuntimeError(f'{cls.__name__} with the given SHA256 already exists')
        name = zfs_shortest_unique_name(sha256, cls._meta_focker_type)
        zfs_create(name, { 'focker:sha256': sha256 })
        return cls.from_sha256(sha256)

    def destroy(self):
        if self.in_use():
            raise RuntimeError(f'This {self.__class__.__name__.lower()} is in use')
        zfs_destroy(self.name)

    @classmethod
    def prune(cls):
        while True:
            lst = cls.list_unused()
            lst = [ ds for ds in lst if not ds.tags ]
            if len(lst) == 0:
                break
            for ds in lst:
                ds.destroy()

    @property
    def is_protected(self):
        protect = self.get_property('focker:protect')
        return (protect != '-')

    def protect(self):
        zfs_protect(self.name)

    def unprotect(self):
        zfs_unprotect(self.name)

    @property
    def path(self):
        return self.mountpoint

    @property
    def origin(self):
        orig = self.get_property('origin')
        orig = '@'.join(orig.split('@')[:-1])
        if not orig:
            return None
        ds = self._meta_class.from_name(orig)
        return ds

    @property
    def origin_tags(self):
        orig = self.origin
        if not orig:
            return None
        return orig.tags

    @property
    def origin_mountpoint(self):
        orig = self.origin
        if not orig:
            return None
        return orig.mountpoint

    @property
    def origin_sha256(self):
        orig = self.origin
        if not orig:
            return None
        return orig.sha256

    @property
    def referred_size(self):
        return self.get_property('refer')

    def set_props(self, props):
        zfs_set_props(self.name, props)

    def get_props(self, props):
        return { k: self.get_property(k) for k in props }

    def get_property(self, propname):
        if self.property_cache is not None:
            return self.property_cache.get(( self.name, propname ), '-')
        return zfs_get_property(self.name, propname)

    @classmethod
    def cache_properties(cls, datasets):
        cache = zfs_properties_cache(cls._meta_focker_type)
        for ds in datasets:
            ds.property_cache = cache

Dataset._meta_class = Dataset
