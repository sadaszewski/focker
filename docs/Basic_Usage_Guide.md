# Focker Basic Usage Guide

```diff
- This document is partly deprecated.
- Please expect an updated version soon.
```

## Prerequisites

In order to get started, you have to prepare a base image for usage with Focker.
In order to do so, you can use the `focker bootstrap` command.

`focker bootstrap` has the following syntax:

```
usage: focker.py bootstrap [-h] [--tags TAGS [TAGS ...]] [--empty]

optional arguments:
  -h, --help            show this help message and exit
  --tags TAGS [TAGS ...], -t TAGS [TAGS ...]
  --empty, -e
  ```

If you use the `--empty` switch, it will create an empty image. This is used
principally for testing and unless you want to set up your image manually, it is
recommended to run `bootstrap` without the `--empty` switch.

The `--tags` parameter lets you specify the tags that the resulting image will
receive. If you do not specify this, the image will be tagged with `freebsd-latest`
and `freebsd-x.y` where `x.y` will be the major and minor version obtained
from a call to `freebsd-version`.

The `bootstrap` command creates a new image and runs `bsdinstall jail` targeting
its mountpoint. It is recommended to install only the base system (no ports, no lib32),
disable all services and do not add any users. The base image will most likely serve as
the starting point for all the other images that you will be building. Pre-made
`Fockerfile` recipes, unless indicated otherwise, will most likely expect a
barebones image as the base.

It is a good practice to account for a base image that has been created by just
clicking through the `bsdinstall jail` installer. Therefore, many `Fockerfile`
recipes will execute the following steps to disable sshd, sendmail, make syslog
listen only locally, enable clearing of `/tmp` and disable writing to
`/var/spool/clientmqueue`:

```
sysrc sshd_enable=NO
sysrc sendmail_enable=NONE
chown root:wheel /var/spool/clientmqueue
chmod 000 /var/spool/clientmqueue
sysrc syslogd_flags="-ss"
sysrc clear_tmp_enable="YES"
```

We can now move on and let you try create your first own customized `Fockerfile`.

## Trivial Example

At the very basic level, Focker can be used simply as a jail building system.
In order to get started you have to create a new directory:

```
mkdir test-focker-build
cd test-focker-build/
```

with a file called `Fockerfile` inside:

`touch Fockerfile`.

Using your editor of choice (`ee` is a good one), you can now put a trivial
directive in `Fockerfile`:

```
base: freebsd-latest
steps: []
```

The `base` directive determines the starting point for your future image.
A starting point is simply a pre-existing image. We will call this image
the parent image. The chain always terminates with an image that doesn't have
a parent. Such an image has to be created manually, by using `focker bootstrap`
or perhaps transferred using `zfs send`/`zfs receive` combo.

Now you are ready to build your first image. Run:

`focker image build .`

The `focker image build` command has the following syntax:

```
usage: focker.py image build [-h] [--tags TAGS [TAGS ...]] [--squeeze]
                             focker_dir

positional arguments:
  focker_dir

optional arguments:
  -h, --help            show this help message and exit
  --tags TAGS [TAGS ...], -t TAGS [TAGS ...]
  --squeeze, -s
```

As you can see, in our call `focker image build .` we have specified only the
`focker_dir` parameter. It tells the Focker which directory contains the
Fockerfile and potentially any additional files that you would like to include
in your build (we will get to this later).

You will see an output similar to the following:

```
Waiting for /var/lock/focker.lock ...
Lock acquired.
poolname: zroot
fname: ./Fockerfile
spec: {'base': 'freebsd-latest', 'steps': []}
base: zroot/focker/images/e4d5685@1 root: zroot/focker/images
```

and if you run `focker image list` you will discover that you are still
stuck only with your pre-existing base image. Why is that?

Since we have specified no `steps` or more precisely we have specified
an empty list of steps, the resulting image has the same checksum as the
base image. This is the case since no modifications have been made and the
image content is identical. To observe an effect, we could still run:

`focker image build . -t test-build`

This will instruct Focker to add a new tag to the resulting image. If you
run `focker image list` now, you should see an output similar to:

```
Tags                                    Size    SHA256    Base
--------------------------------------  ------  --------  -------
freebsd-latest freebsd-11.2 test-build  266M    e4d5685   -
```

Congratulations! Your first image has been tagged. We can now start
filling the `steps` list to create something more useful.
