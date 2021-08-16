# API

A couple of examples follow.

## Build an image

```python
from focker.core import ImageBuilder

bld = ImageBuilder(focker_dir='/path/to/some/directory', squeeze=True)
im = bld.build()
im.add_tags([ 'my-fancy-image-tag' ])
```

## Create and start a jail

```python
from focker.core import ( CloneImageJailSpec, OSJailSpec )

spec = CloneImageJailSpec.from_dict({ 'image': 'my-fancy-image-tag' })
ospec = OSJailSpec.from_jailspec(spec)
jail = ospec.add()
jail.start()
```

## Create a volume
```python
from focker.core import Volume

v = Volume.create()
v.add_tags([ 'my-fancy-volume-tag' ])
```
