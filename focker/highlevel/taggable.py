from ..zfs import zfs_list, \
    zfs_tag, \
    zfs_untag


class Taggable:
    _meta_class = None
    _meta_list_columns = ['name', 'mountpoint', 'focker:sha256', 'focker:tags', 'rdonly']
    _meta_focker_type = 'image'
    _meta_zfs_type = 'filesystem'
    __init_key = object()

    def __init__(self, **kwargs):
        if 'init_key' not in kwargs or kwargs['init_key'] != self.__init_key:
            raise RuntimeError(f'{self.__class__.__name__} must be created using one of the factory methods')

        self.name = kwargs['name']
        self.sha256 = kwargs['sha256']
        self.tags = set(kwargs['tags'])
        self.mountpoint = kwargs['mountpoint']
        self.is_finalized = kwargs['is_finalized']

    @classmethod
    def from_predicate_handle_corner_cases(cls, lst):
        if len(lst) == 0:
            raise RuntimeError(f'{cls.__name__} not found')
        if len(lst) > 1:
            raise RuntimeError(f'Ambiguous {cls.__name__.lower()} reference')

    @classmethod
    def from_predicate(cls, pred):
        lst = zfs_list(cls._meta_list_columns,
            focker_type=cls._meta_focker_type, zfs_type=cls._meta_zfs_type)
        lst = [ e for e in lst if pred(e) ]
        # print(lst)
        cls.from_predicate_handle_corner_cases(lst)
        name, mountpoint, sha256, tags, rdonly, *_ = lst[0]
        tags = tags.split(' ')
        is_finalized = (rdonly == 'on')
        return cls._meta_class(init_key=cls.__init_key, name=name, sha256=sha256,
            tags=tags, mountpoint=mountpoint, is_finalized=is_finalized)

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
    def from_any_id(cls, id_: str, strict=False):
        if strict:
            return cls.from_predicate(lambda e: \
                id_ in e[3].split(' ') or e[2] == id_)
        else:
            return cls.from_predicate(lambda e: \
                any(t.startswith(id_) for t in e[3].split(' ')) or \
                e[2].startswith(id_))

    def add_tags(self, tags):
        zfs_untag(tags, focker_type=self._meta_focker_type)
        zfs_tag(self.name, tags)
        self.tags = self.tags.union(tags)

    def remove_tags(self, tags):
        if any(t not in self.tags for t in tags):
            raise RuntimeError(f'This {self.__class__.__name__.lower()} does not seem to be tagged with all the specified tags')
        zfs_untag(tags, focker_type=self._meta_focker_type)
        self.tags = self.tags.difference(tags)

    def path(self):
        return self.mountpoint

Taggable._meta_class = Taggable
