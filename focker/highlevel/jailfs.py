from .image import Image


class JailFs:
    __init_key = object()

    def __init__(self, **kwargs):
        if kwargs.get('init_key') != JailFs.__init_key:
            raise RuntimeError('JailFs must be created using one of the factory methods')

    @staticmethod
    def from_image(image: Image):
        raise NotImplementedError
