from .taggable import Taggable


class Volume(Taggable):
    _meta_focker_type = 'volume'

    def __init__(self, **kwargs):
        Taggable.__init__(self, **kwargs)

Volume._meta_class = Volume
