import os
from ... import yaml
from functools import reduce
from .steps import create_step
from .image import Image


def validate(spec):
    if 'base' not in spec:
        raise RuntimeError('Missing base image specification')

    if ('steps' in spec) + ('facets' in spec) != 1:
        raise RuntimeError('Exactly one of "steps" or "facets" must be specified')


class ImageBuilder:
    def __init__(self, focker_dir, squeeze=False):
        self.focker_dir = focker_dir
        self.squeeze = squeeze

    def build(self) -> Image:
        if not os.path.exists(os.path.join(self.focker_dir, 'Fockerfile')):
            raise RuntimeError('Fockerfile not found in the specified directory')

        with open(os.path.join(self.focker_dir, 'Fockerfile')) as f:
            spec = yaml.safe_load(f)

        validate(spec)

        if 'steps' in spec:
            im = self.process_steps(spec)
        else:
            im = self.process_facets(spec)

        return im

    def process_steps(self, spec) -> Image:
        steps = spec['steps']

        if isinstance(steps, list):
            steps = [ [ st ] for st in steps ]
        else:
            steps = [ steps[k] for k in sorted(steps.keys()) ]

        if self.squeeze:
            steps = [ reduce(list.__add__, steps) ]

        base_im = Image.from_any_id(spec['base'], strict=True)

        sha256 = base_im.sha256
        im = base_im
        for group in steps:
            for st in group:
                st = create_step(st, self.focker_dir)
                sha256 = st.hash(sha256)
            if Image.exists_sha256(sha256):
                im = Image.from_sha256(sha256)
                continue
            im = Image.clone_from(im, sha256=sha256)
            try:
                for st in group:
                    st = create_step(st, self.focker_dir)
                    st.execute(im)
            except:
                im.destroy()
                raise
            im.finalize()

        return im

    def process_facets(self, spec) -> Image:
        raise NotImplementedError
