from ..zfs import zfs_list, \
    zfs_clone, \
    zfs_mountpoint, \
    zfs_set_props, \
    zfs_tag, \
    zfs_untag
from ..zfs2 import zfs_shortest_unique_name, \
    zfs_snapshot, \
    zfs_exists_props
from ..snapshot import new_snapshot
from ..misc import find_prefix

Image='Image'

class Image:
    __init_key = object()

    def __init__(self, **kwargs):
        if 'init_key' not in kwargs or kwargs['init_key'] != self.__init_key:
            raise RuntimeError('Image must be created using one of the factory methods')

        self.name = kwargs['name']
        self.sha256 = kwargs['sha256']
        self.tags = set(kwargs['tags'])
        self.mountpoint = kwargs['mountpoint']
        self.is_finalized = kwargs['is_finalized']

    @staticmethod
    def handle_from_predicate_corner_cases(lst):
        if len(lst) == 0:
            raise RuntimeError('Image not found')
        if len(lst) > 1:
            raise RuntimeError('Ambiguous image reference')

    @staticmethod
    def from_predicate(pred):
        lst = zfs_list(['name', 'mountpoint', 'focker:sha256', 'focker:tags', 'rdonly'],
            focker_type='image', zfs_type='filesystem')
        lst = [ e for e in lst if pred(e) ]
        # print(lst)
        Image.handle_from_predicate_corner_cases(lst)
        name, mountpoint, sha256, tags, rdonly, *_ = lst[0]
        tags = tags.split(' ')
        is_finalized = (rdonly == 'on')
        return Image(init_key=Image.__init_key, name=name, sha256=sha256,
            tags=tags, mountpoint=mountpoint, is_finalized=is_finalized)

    @staticmethod
    def from_sha256(sha256: str):
        return Image.from_predicate(lambda e: e[2] == sha256)

    @staticmethod
    def from_tag(tag: str):
        return Image.from_predicate(lambda e: tag in e[3].split(' '))

    @staticmethod
    def from_partial_sha256(sha256: str):
        return Image.from_predicate(lambda e: e[2].startswith(sha256))

    @staticmethod
    def from_partial_tag(tag: str):
        return Image.from_predicate(lambda e: any(t.startswith(tag) for t in e[3].split(' ')))

    @staticmethod
    def from_any_id(id_: str, strict=False):
        if strict:
            return Image.from_predicate(lambda e: \
                id_ in e[3].split(' ') or e[2] == id_)
        else:
            return Image.from_predicate(lambda e: \
                any(t.startswith(id_) for t in e[3].split(' ')) or \
                e[2].startswith(id_))

    @staticmethod
    def from_base(base: Image, sha256: str) -> Image:
        if not base.is_finalized:
            raise RuntimeError('Base must be finalized')
        if zfs_exists_props({ 'focker:sha256': sha256 }, focker_type='image',
            zfs_type='filesystem'):
            raise RuntimeError('Image with specified SHA256 already exists')
        name = zfs_shortest_unique_name(sha256, focker_type='image')
        zfs_clone(base.snapshot_name(), name, { 'focker:sha256': sha256 })
        mountpoint = zfs_mountpoint(name)
        return Image(init_key=Image.__init_key, name=name, sha256=sha256,
            tags=[], mountpoint=mountpoint, is_finalized=False)

    def apply_spec(self):
        raise NotImplementedError

    def finalize(self):
        zfs_set_props(self.name, { 'rdonly': 'on' })
        zfs_snapshot(self.snapshot_name())
        self.is_finalized = True

    def create(self):
        raise NotImplementedError

    def path(self):
        return self.mountpoint

    def snapshot_name(self):
        return self.name + '@1'

    def add_tags(self, tags):
        zfs_untag(tags, focker_type='image')
        self.tags = self.tags.union(tags)
        zfs_tag(self.name, tags)

    def remove_tags(self, tags):
        if any(t not in self.tags for t in tags):
            raise RuntimeError('This image does not seem to be tagged with all the specified tags')
        zfs_untag(tags, focker_type='image')
        self.tags = self.tags.difference(tags)
