# API

Focker 2 has been redesigned from the ground up to be more modular, better structured and create a solid foundation for future development. At the top level, the code is grouped into 4 major categories - **cmdmodule**, **core**, **jailconf** and **misc**, which bring together the business logic responsible for respectively: CLI functionality delivered as plugins, image/volume/jail management, roundtrip /etc/jail.conf parser and miscellaneous/helper functions.

The most fundamental part of the API to understand is the **focker.core** module. It is very likely that regardless of the functionality you are trying to achieve, you will be compelled to reach out to **focker.core** on one or more occassions. A couple of examples follow.

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

## Create an image, volume and two dependent jails
```python
from focker.core import ( Volume, CloneImageJailSpec, OSJailSpec )
im = Image.clone_from(Image.from_tag('freebsd-latest'))
v = Volume.create()
spec = CloneImageJailSpec.from_dict({ 'image': 'freebsd-latest' })
ospec = OSJailSpec.from_jailspec(spec)
jail_1 = ospec.add()
spec = CloneImageJailSpec.from_dict({ 'image': 'freebsd-latest',
  'depend': [ jail_1.name ], 'mounts': [ [ v, '/mnt' ] ]  })
ospec = OSJailSpec.from_jailspec(spec)
jail_2 = ospec.add()
jail_2.add_tags([ 'jail-2' ])
```
