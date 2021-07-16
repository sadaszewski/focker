from .process import focker_subprocess_check_output, \
    focker_subprocess_run
from .jailspec import JailSpec
from .osjailspec import OSJailSpec
from .jailfs import JailFs
from .image import Image
import os
import ruamel.yaml as yaml


class PrePostCommandManager:
    def __init__(self, pre_command, post_command):
        self.pre_command = pre_command
        self.post_command = post_command

    def __enter__(self):
        focker_subprocess_check_output(self.pre_command)

    def __exit__(self, exc_type, exc_val, exc_tb):
        focker_subprocess_check_output(self.post_command)


def default_jail_run(im, command):
    feed = {
        'exec.start': '',
        'exec.stop': ''
    }
    if isinstance(im, JailFs):
        feed['jailfs'] = im
    elif isinstance(im, Image):
        feed['image'] = im
    else:
        raise TypeError('Expected JailFs or Image')
    spec = JailSpec.from_dict(feed)
    ospec = OSJailSpec.from_jailspec(spec)
    ospec.add()
    focker_subprocess_check_output(['jail', '-c', ospec.name])
    try:
        focker_subprocess_run(['jexec', ospec.name, '/bin/sh', '-c', command])
    finally:
        focker_subprocess_check_output(['jail', '-r', ospec.name])
        ospec.remove()


def get_path_and_name(spec, mode='attach'):
    if mode not in ['create', 'attach']:
        raise RuntimeError('Mode can be "create" or "attach" only')

    if ('path' in spec) + ('image' in spec) + ('jailfs' in spec) != 1:
        raise RuntimeError('Exactly one of "path", "image" or "jailfs" was expected')

    if (mode == 'create' and 'image' not in spec):
        raise RuntimeError('Create mode can be used only with an image')

    if 'image' in spec:
        path = spec['image']
        if isinstance(path, str):
            path = Image.from_any_id(path, strict=True)
        if mode == 'create':
            path = JailFs.clone_from(path)
        path = path.path
        _, name = os.path.split(path)
        name = name if mode == 'create' else 'img_' + name
    elif 'jailfs' in spec:
        path = spec['jailfs']
        if isinstance(path, str):
            path = JailFs.from_any_id(path, strict=True)
        path = path.path
        _, name = os.path.split(path)
    else:
        path = spec['path']
        name = hashlib.sha256(os.path.abspath(path).encode('utf-8')).hexdigest()[:7]
        name = 'raw_' + name
        return path

    return path, name
