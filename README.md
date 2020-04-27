# Focker

## Introduction

Focker is a FreeBSD image orchestration tool in the vein of Docker.

## Installation

In order to use Focker you need a ZFS pool available in your FreeBSD installation.

### Installing the Python package from PyPi

Run:

```bash
pip install focker
```

### Installing the Python package from GitHub

Run:

```bash
git clone https://github.com/sadaszewski/focker.git
cd focker/
python setup.py install
```

or (if you want an uninstaller):

```bash
git clone https://github.com/sadaszewski/focker.git
cd focker/
python setup.py sdist
pip install dist/focker-0.9.tgz
```

### Setting up ZFS

Upon first execution of the `focker` command, Focker will automatically create the necessary directories and ZFS datasets. You just need to exclude the unlikely case that you are already using /focker in your filesystem hierarchy. The layout after initialization will look the following:

```
/focker
/focker/images
/focker/jails
/focker/volumes
```

`images`, `jails`, and `volumes` have corresponding ZFS datasets with `canmount=off` so that they serve as mountpoint anchors for child entries.

### Preparing base image

To bootstrap the images system you need to install FreeBSD in jail mode to a ZFS dataset placed in /focker/images and provide two user-defined properties - `focker:sha256` and `focker:tags`. One way to achieve this would be the following:

```bash
TAGS="freebsd-latest freebsd-$(freebsd-version | cut -d'-' -f1)"
VERSION="FreeBSD $(freebsd-version)"
SHA256=$(echo -n ${VERSION} | sha256)
NAME=${SHA256:0:7}
zfs create -o focker:sha256=${SHA256} -o focker:tags="${TAGS}" zroot/focker/images/${NAME}
bsdinstall jail /focker/images/${NAME}
zfs set readonly=on zroot/focker/images/${NAME}
zfs snapshot zroot/focker/images/${NAME}@1
```

## Usage

At this point, Focker is ready to use.

### `focker` command syntax

The `focker` command is the single entrypoint to all of the Focker's functionality. The overview of its syntax is presented below as a tree where the `focker` command is the root, the first level of descendants represents the choice of Level 1 mode (`image`, `jail`, `volume` or `compose`), the second level - the Level 2 mode (dependent on L1 mode) and the final third level lists required and optional arguments specific to the given combination of L1/L2 modes.

```
focker
|- image|img|im|i
|  |- build|b
|  |  |- FOCKER_DIR
|  |  `- --tags|-t TAG [...TAG]
|  |- tag|t
|  |  |- REFERENCE
|  |  `- TAG [...TAG]
|  |- untag|u
|  |  `- TAG [...TAG]
|  |- list|ls|l
|  |  `- --full-sha256|-f
|  |- prune|p
|  `- remove|r
|     |- REFERENCE
|     `- --remove-dependents|-R
|- jail|j
|  |- create|c
|  |  |- IMAGE
|  |  |- --command|-c COMMAND (default: /bin/sh)
|  |  |- --env|-e VAR1:VALUE1 [...VARN:VALUEN]
|  |  |- --mounts|-m FROM1:ON1 [...FROMN:ONN]
|  |  `- --hostname|-n HOSTNAME
|  |- start|s
|  |  `- REFERENCE
|  |- stop|S
|  |  `- REFERENCE
|  |- remove|r
|  |  `- REFERENCE
|  |- exec|e
|  |  |- REFERENCE
|  |  `- [...COMMAND]
|  |- oneshot|o
|  |  `- IMAGE
|  |  `- --env|-e VAR1:VALUE1 [...VARN:VALUEN]
|  |  `- --mounts|-m FROM1:ON1 [...FROMN:ONN]
|  |  `- [...COMMAND]
|  |- list|ls|l
|  |  `- --full-sha256|-f
|  |- tag|t
|  |  |- REFERENCE
|  |  `- TAG [...TAG]
|  |- untag|u
|  |  `- TAG [...TAG]
|  `- prune|p
|     `- --force|-f
|- volume
|  |- create
|  |  `- --tags|-t TAG [...TAG]
|  |- prune
|  |- list
|  |  `- --full-sha256|-f
|  |- tag
|  |  |- REFERENCE
|  |  `- TAG [...TAG]
|  `- untag
|     `- TAG [...TAG]
`- compose
   |- build
   |  `- FILENAME
   `- run
      |- FILENAME
      `- COMMAND
```

Individual combinations are briefly described below:

#### focker image

The `focker image` mode groups commands related to Focker images.

##### build FOCKER_DIR [--tags TAG [...TAG]]

Build a Focker image according to the specification in a Fockerfile present in the specified FOCKER_DIR. Fockerfile syntax is very straightforward and explained below.

##### tag REFERENCE TAG [...TAG]

Applies one or more tags to the given image. REFERENCE can be the SHA256 of an image or one of its existing tags. It can be just a few first characters as long as they are unambiguous.

##### untag TAG [...TAG]

Removes one or more image tags.

##### list [--full-sha256|-f]

Lists existing Focker images, optionally with full SHA256 checksums (instead of the default 7 first characters).

##### prune

Greedily removes existing Focker images without tags and without dependents.

##### remove REFERENCE

Removes the specified image.

#### focker jail

##### create

##### start

##### stop

##### remove

##### exec

##### oneshot

##### list

##### tag

##### untag

##### prune

#### focker volume

##### create

##### prune

##### list

##### tag

##### untag

#### focker compose

##### build

##### run
