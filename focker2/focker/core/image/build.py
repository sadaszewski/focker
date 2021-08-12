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

        if not all(isinstance(st, list) for st in steps):
            raise TypeError('Expected list/s of steps, not single step/s')

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
        steps = []

        for fname in spec['facets']:
            with open(os.path.join(self.focker_dir, fname)) as f:
                data = yaml.safe_load(f)

            if 'steps' not in data:
                raise KeyError(f'One of the facets ({fname}) is missing the "steps" key')

            steps.append(data['steps'])

        if not all(isinstance(fa, steps[0].__class__) for fa in steps):
            raise TypeError('Steps in all facets must be specified using the same convention (list or dict)')

        if isinstance(steps[0], list):
            steps = reduce(list.__add__, steps, [])
        elif isinstance(steps[0], dict):
            steps = reduce(lambda a, b: { **a, **b }, steps, {})
        else:
            raise TypeError(f'Unsupported steps convention ({steps[0].__class__.__name__})')

        spec = dict(spec)
        del spec['facets']
        spec['steps'] = steps

        return self.process_steps(spec)
