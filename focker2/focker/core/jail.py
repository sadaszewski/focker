from .jailspec import JailSpec
from .osjailspec import OSJailSpec
from .jailfs import JailFs
from .image import Image
from ..misc import load_jailconf, \
    jailconf_unquote


class Jail:
    _init_key = object()

    def __init__(self, init_key=None, **kwargs):
        if init_key != self._init_key:
            raise RuntimeError('Jail must be created using one of the constructor methods')

        self.jail_name = kwargs['jail_name']
        self.fobject = kwargs['fobject']

    @staticmethod
    def validate(spec, mode):
        if mode not in [ 'create', 'attach' ]:
            raise RuntimeError('Mode must be "create" or "attach"')

        if ('path' in spec) + ('jailfs' in spec) + ('image' in spec) != 1:
            raise RuntimeError('Exactly one of "path", "jailfs" or "image" expected')

        if 'path' in spec and mode == 'create':
            raise RuntimeError('"path" is supported in "attach" mode only')

        if 'jailfs' in spec and mode == 'create':
            raise RuntimeError('"jailfs" is supported in "attach" mode only')

    @staticmethod
    def from_dict(spec, mode='create'):
        Jail.validate_dict(spec)
        spec = dict(spec)

        if 'image' in spec and mode == 'create':
            im = spec['image']
            if not isinstance(im, Image):
                im = Image.from_any_id(im, strict=True)
            jfs = JailFs.clone_from(im)
            del spec['image']
            spec['jailfs'] = jfs

        jspec = JailSpec.from_dict(spec)
        ospec = OSJailSpec.from_jailspec(spec)
        ospec.add()
        return Jail(init_key=Jail._init_key, jail_name=ospec.name,
            fobject=jspec.fobject)

    @staticmethod
    def from_fobject(fobj):
        conf = load_jailconf()
        for k, blk in conf.items():
            if jailconf_unquote(blk.get('path')) == fobj.path:
                return Jail(init_key=Jail._init_key, jail_name=k, fobject=fobj)
        return None

    @staticmethod
    def for_image_building(im):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    def exec(self, command):
        raise NotImplementedError

    def remove_from_jailconf(self):
        raise NotImplementedError

    @staticmethod
    def list(cls=JailFs):
        return [ Jail.from_fobject(fobj) for fobj in cls.list() ]

    @staticmethod
    def untag(tags, cls=JailFs):
        cls.untag(tags)

    def __getattr__(self, attr):
        if hasattr(self.fobject, attr):
            return getattr(self.fobject, attr)
        raise AttributeError
