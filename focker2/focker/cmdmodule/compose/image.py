from ...core import ImageBuilder


def build_images(spec, squeeze=False):
    for tag, focker_dir in spec.items():
        bld = ImageBuilder(focker_dir, squeeze=squeeze)
        im = bld.build()
        im.add_tags([ tag ])
        print(f'Created image {im.name} mounted at {im.mountpoint} with tags: {", ".join(im.tags)}')
