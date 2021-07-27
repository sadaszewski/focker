import os
import ruamel.yaml as yaml
from functools import reduce
from .steps import create_step
from ...core.image import Image


def validate(spec):
    if 'base' not in spec:
        raise RuntimeError('Missing base image specification')

    if ('steps' in spec) + ('facets' in spec) != 1:
        raise RuntimeError('Exactly one of "steps" or "facets" must be specified')


def process_steps(spec, args, src_dir):
    steps = spec['steps']

    if isinstance(steps, list):
        steps = [ [ st ] for st in steps ]
    else:
        steps = [ steps[k] for k in sorted(steps.keys()) ]

    if args.squeeze:
        steps = [ reduce(list.__add__, steps) ]

    base_im = Image.from_any_id(spec['base'], strict=True)

    sha256 = base_im.sha256
    im = base_im
    for group in steps:
        for st in group:
            st = create_step(st, src_dir)
            sha256 = st.hash(sha256, args=args)
        if Image.exists_sha256(sha256):
            im = Image.from_sha256(sha256)
            continue
        im = Image.clone_from(im, sha256=sha256)
        try:
            for st in group:
                st = create_step(st, src_dir)
                st.execute(im, args=args)
        except:
            im.destroy()
            raise
        im.finalize()

    return im


def process_facets(spec):
    raise NotImplementedError


def cmd_image_build(args):
    if not os.path.exists(os.path.join(args.focker_dir, 'Fockerfile')):
        raise RuntimeError('Fockerfile not found in the specified directory')

    with open(os.path.join(args.focker_dir, 'Fockerfile')) as f:
        spec = yaml.safe_load(f)

    validate(spec)

    if 'steps' in spec:
        im = process_steps(spec, args, args.focker_dir)
    else:
        im = process_facets(spec)

    im.add_tags(args.tags)

    print(f'Created {im.name}, mounted at {im.path}, with tags: {", ".join(args.tags)}')
