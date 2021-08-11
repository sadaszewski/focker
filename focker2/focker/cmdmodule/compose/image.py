from ...core import ImageBuilder
import os


def build_images(spec, spec_dir, squeeze=False):
    for tag, focker_dir in spec.items():
        focker_dir = os.path.join(spec_dir, focker_dir)
        bld = ImageBuilder(focker_dir, squeeze=squeeze)
        im = bld.build()
        im.add_tags([ tag ])
        print(f'Created image {im.name} mounted at {im.mountpoint} with tags: {", ".join(im.tags)}')
