from ..zfs import zfs_list, \
    zfs_clone, \
    zfs_mountpoint, \
    zfs_set_props
from ..zfs2 import zfs_shortest_unique_name, \
    zfs_snapshot
from ..snapshot import new_snapshot
from ..misc import find_prefix

Image='Image'

class Image:
    __init_key = object()

    def __init__(self, init_key, name, sha256, mountpoint, is_finalized):
        if not init_key == self.__init_key:
            raise RuntimeError('Image must be created using one of the factory methods')

        self.name = name
        self.sha256 = sha256
        self.mountpoint = mountpoint
        self.is_finalized = is_finalized

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
        name, mountpoint, sha256, _, rdonly, *_ = lst[0]
        is_finalized = (rdonly == 'on')
        return Image(Image.__init_key, name=name, sha256=sha256,
            mountpoint=mountpoint, is_finalized=is_finalized)

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
    def from_any_id(id_: str, strict=False):
        return Image.from_predicate(lambda e: \
            id_ in e[3].split(' ') or \
            ( e[2] == id_ if strict else e[2].startswith(id_) ) )

    @staticmethod
    def from_base(base: Image, sha256: str) -> Image:
        if not base.is_finalized:
            raise RuntimeError('Base must be finalized')
        name = zfs_shortest_unique_name(sha256, focker_type='image')
        zfs_clone(base.snapshot_name(), name, { 'focker:sha256': sha256 })
        mountpoint = zfs_mountpoint(name)
        return Image(Image.__init_key, name=name, sha256=sha256,
            mountpoint=mountpoint, is_finalized=False)

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
