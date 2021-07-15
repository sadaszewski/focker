from .dataset import Dataset


class Volume(Dataset):
    _meta_focker_type = 'volume'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

Volume._meta_class = Volume
