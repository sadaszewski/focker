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

Upon first execution of the `focker` command, Focker will automatically create the necessary directories and ZFS datasets. You just need to exclude the unlikely case that you are already using `/focker` in your filesystem hierarchy. The layout after initialization will look the following:

```
/focker
/focker/images
/focker/jails
/focker/volumes
```

`images`, `jails`, and `volumes` have corresponding ZFS datasets with `canmount=off` so that they serve as mountpoint anchors for child entries.

### Preparing base image

To bootstrap the images system you need to install FreeBSD in jail mode to a ZFS dataset placed in `/focker/images` and provide two user-defined properties - `focker:sha256` and `focker:tags`. One way to achieve this would be the following (using Bash shell):

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

#### focker image|img|im|i

The `focker image` mode groups commands related to Focker images.

##### build|b FOCKER_DIR [--tags TAG [...TAG]]

Build a Focker image according to the specification in a Fockerfile present in the specified FOCKER_DIR. Fockerfile syntax is very straightforward and explained below.

##### tag|t REFERENCE TAG [...TAG]

Applies one or more tags to the given image. REFERENCE can be the SHA256 of an image or one of its existing tags. It can be just a few first characters as long as they are unambiguous.

##### untag|u TAG [...TAG]

Removes one or more image tags.

##### list|ls|l [--full-sha256|-f]

Lists existing Focker images, optionally with full SHA256 checksums (instead of the default 7 first characters).

##### prune|p

Greedily removes existing Focker images without tags and without dependents.

##### remove|r REFERENCE

Removes the specified image.

#### focker jail|j

The `focker jail` mode groups commands related to Focker-managed jails.

##### create|c IMAGE [--command|-c COMMAND] [--env|-e VAR1:VALUE1 [...VARN:VALUEN]] [--mounts|-m FROM1:ON1 [...FROMN:ONN]] [--hostname|-n HOSTNAME]

Creates a new Focker-managed jail. A jail consists of a clone of the given `IMAGE` and an entry in `/etc/jail.conf`. The configuration entry uses `exec.prestart` and `exec.start` to specify how the runtime environment (mounts and environmental variables) should be set up. It also calls `COMMAND` as last in `exec.start`. If not specified `COMMAND` defaults to `/bin/sh`. The hostname can be specified using the `HOSTNAME` parameter. Mounts and environment variables are provided as tuples separated by a colon (:). The environmental variable specification consists of variable name followed by variable value. The mount specification consists of the "from path", followed by the "on path". "From path" can be a local system path or a volume name.

##### start|s REFERENCE

Starts the given jail specified by `REFERENCE`. `REFERENCE` can be the SHA256 of an existing jail or one of its existing tags. It can be just a few first characters as long as they are unambiguous. This command is equivalent of calling `jail -c`.

##### stop|S REFERENCE

Stops the given jail specified by `REFERENCE`. This command is equivalent to calling `jail -r`.

##### remove|r REFERENCE

Removes the given jail specified by `REFERENCE`. The jail is stopped if running, any filesystems mounted under its root directory are unmounted, its ZFS dataset and entry in `/etc/jail.conf` are removed.

##### exec|e REFERENCE [...COMMAND]

Executes given `COMMAND` (or `/bin/sh` if not specified) in the given running jail specified by `REFERENCE`. This command is the equivalent of calling `jexec`.

##### oneshot|o IMAGE [--env|-e VAR1:VALUE1 [...VARN:VALUEN]] [--mounts|-m FROM1:ON1 [...FROMN:ONN]] [...COMMAND]

Create a new one-time Focker-managed jail. The syntax and logic is identical to `focker jail create`, the difference being that the hostname cannot be specified and that the jail will be automatically removed when the `COMMAND` exits.

Example: `focker jail oneshot freebsd-latest -e FOO:bar -- ls -al`

##### list|ls|l

Lists Focker-managed jails. For running jails their JIDs will be displayed.

##### tag REFERENCE TAG [...TAG]

Applies one or more tags to the given jail. REFERENCE can be the SHA256 of a jail or one of its existing tags. It can be just a few first characters as long as they are unambiguous.

##### untag TAG [...TAG]

Removes one or more jail tags.

##### prune

Removes existing Focker jails without tags.

#### focker volume

The `focker volume` mode groups commands related to Focker volumes.

##### create [--tags|-t TAG [...TAG]]

Create a new Focker volume optionally tagged with the given `TAG`s.

##### prune

Removes existing Focker volumes without tags.

##### list [--full-sha256|-f]

Lists existing Focker volumes. Full SHA256 is displayed if the `-f` switch is used, otherwise only the first 7 characters will be shown.

##### tag REFERENCE TAG [...TAG]

Applies one or more tags to the given volume. REFERENCE can be the SHA256 of a volume or one of its existing tags. It can be just a few first characters as long as they are unambiguous.

##### untag TAG [...TAG]

Removes one or more volume tags.

#### focker compose

The `focker compose` mode groups commands related to Focker composition files - `focker-compose.yml`.

##### build

##### run

### `Fockerfile` syntax

A sample `Fockerfile` is pasted below.

```yaml
base: freebsd-latest

steps:
  - copy:
    - [ '/tmp/x', '/etc/x' ]
    - [ 'files/y', '/etc/y' ]
  - run: |
      pkg install -y python3 && \
      pkg install -y py37-pip && \
      pkg install -y py37-yaml && \
      pkg install -y py37-certbot && \
      mkdir -p /persist/etc/ssh && \
      sed -i '' -e 's/\/etc\/ssh\/ssh_host_/\/persist\/etc\/ssh\/ssh_host_/g' /etc/rc.d/sshd && \
      sed -i '' -e 's/\/etc\/ssh\/ssh_host_/\/persist\/etc\/ssh\/ssh_host_/g' /etc/ssh/sshd_config && \
      sed -i '' -e 's/#HostKey/HostKey/g' /etc/ssh/sshd_config
```

### `focker-compose.yml` syntax

A sample composition file illustrating all of the principles is pasted below.

```yaml
images:
  wordpress-5: /path/to/wordpress_5_focker_dir

jails:
  wordpress:
    image: wordpress-5
    env:
      SITE_NAME: Test site
    mounts:
      wp-volume2: /mnt/volume2
      wp-volume1: /mnt/volume1
    ip4.addr: 127.0.1.1
    interface: lo1

volumes:
  wp-volume1: {}
  wp-volume2: {}
  wp-backup: {}

commands:
  backup:
    jail: wordpress
    command: |
      mysqldump >/mnt/volume2/backup.sql
    mounts:
      wp-backup: /mnt/backup

  restore:
    jail: wordpress
    command: |
      mysql </mnt/volume2/backup.sql
    mounts:
      wp-backup: /mnt/backup
```

#### Images

#### Jails

#### Volumes

#### Commands
