from ..zfs import zfs_list


class Image:
    def __init__(self, sha256=None, mountpoint=None):
        self.sha256 = sha256
        self.mountpoint = mountpoint

    @staticmethod
    def handle_from_predicate_corner_cases(lst):
        if len(lst) == 0:
            raise RuntimeError('Image not found')
        if len(lst) > 1:
            raise RuntimeError('Ambiguous image reference')

    @staticmethod
    def from_predicate(pred):
        lst = zfs_list(['name', 'mountpoint', 'focker:sha256', 'focker:tags'],
            focker_type='image', zfs_type='filesystem')
        lst = [ e for e in lst if pred(e) ]
        Image.handle_from_predicate_corner_cases(lst)
        name, mountpoint, sha256, *_ = lst[0]
        return Image(sha256=sha256, mountpoint=mountpoint)

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

    def create(self):
        pass

    def path(self):
        return self.mountpoint
