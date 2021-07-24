from .zfs import *


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
        res = zfs_get_property(self.name, 'rdonly')
        return (res == 'on')

    @property
    def tags(self):
        res = zfs_get_property(self.name, 'focker:tags')
        res = res.split(' ')
        res = [ t for t in res if t != '-' ]
        return set(res)

    @property
    def snapshot_name(self):
        return self.name + '@1'

    @property
    def size(self):
        return zfs_get_property(self.name, 'used')

    @classmethod
    def list(cls):
        res = zfs_list(cls._meta_list_columns, focker_type=cls._meta_focker_type,
            zfs_type=cls._meta_zfs_type)
        res = [ cls._meta_class(init_key=cls._init_key, name=name, sha256=sha256,
            mountpoint=mountpoint)
                for name, mountpoint, sha256, *_ in res ]
        return res

    @classmethod
    def from_predicate_handle_corner_cases(cls, lst):
        if len(lst) == 0:
            raise RuntimeError(f'{cls.__name__} not found')
        if len(lst) > 1:
            raise RuntimeError(f'Ambiguous {cls.__name__.lower()} reference')

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
    def from_predicate(cls, pred):
        lst = zfs_list(cls._meta_list_columns,
            focker_type=cls._meta_focker_type, zfs_type=cls._meta_zfs_type)
        lst = [ e for e in lst if pred(e) ]
        # print(lst)
        cls.from_predicate_handle_corner_cases(lst)
        name, mountpoint, sha256, *_ = lst[0]
        return cls._meta_class(init_key=cls._init_key, name=name, sha256=sha256,
            mountpoint=mountpoint)

    @classmethod
    def from_sha256(cls, sha256: str):
        return cls.from_predicate(lambda e: e[2] == sha256)

    @classmethod
    def from_tag(cls, tag: str):
        return cls.from_predicate(lambda e: tag in e[3].split(' '))

    @classmethod
    def from_partial_sha256(cls, sha256: str):
        return cls.from_predicate(lambda e: e[2].startswith(sha256))

    @classmethod
    def from_partial_tag(cls, tag: str):
        return cls.from_predicate(lambda e: any(t.startswith(tag) for t in e[3].split(' ')))

    @classmethod
    def from_any_id(cls, id_: str, strict=True):
        if strict:
            return cls.from_predicate(lambda e: \
                id_ in e[3].split(' ') or e[2] == id_)
        else:
            return cls.from_predicate(lambda e: \
                any(t.startswith(id_) for t in e[3].split(' ')) or \
                e[2].startswith(id_))

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
        lst = [ ds for ds in self.list_unused() \
            if ds.name == self.name ]
        return ( len(lst) == 0 )

    @classmethod
    def list_unused(cls):
        raise NotImplementedError

    @classmethod
    def create(cls, sha256=None):
        if sha256 is None:
            sha256 = random_sha256_hexdigest()
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
        protect = zfs_get_property(self.name, 'focker:protect')
        return (protect != '-')

    def protect(self):
        zfs_protect(self.name)

    def unprotect(self):
        zfs_unprotect(self.name)

    @property
    def path(self):
        return self.mountpoint

    def set_props(self, props):
        zfs_set_props(self.name, props)

    def get_props(self, props):
        return { k: zfs_get_property(self.name, k) for k in props }

Dataset._meta_class = Dataset
