from .dataset import Dataset


Image='Image'

class Image(Dataset):
    _meta_focker_type = 'image'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def from_base(base: Image, sha256: str) -> Image:
        return Image.clone_from(base)

    def apply_spec(self):
        raise NotImplementedError

    def create(self):
        raise NotImplementedError

Image._meta_class = Image
Image._meta_cloneable_from = Image
