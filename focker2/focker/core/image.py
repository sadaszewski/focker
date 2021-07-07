from .taggable import Taggable
from .cloneable import Cloneable


Image='Image'

class Image(Taggable, Cloneable):
    _meta_focker_type = 'image'

    def __init__(self, **kwargs):
        Taggable.__init__(self, **kwargs)
        Cloneable.__init__(self, **kwargs)

    @staticmethod
    def from_base(base: Image, sha256: str) -> Image:
        return Image.clone_from(base)

    def apply_spec(self):
        raise NotImplementedError

    def create(self):
        raise NotImplementedError

Image._meta_class = Image
Image._meta_cloneable_from = Image