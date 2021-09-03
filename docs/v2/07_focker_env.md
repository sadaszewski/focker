# Focker Environment (FEnv) Variables

FEnv variables can parametrize processes of image and composition building. They can be specified at three levels (in order of increasing precedence) - Fockerfile, focker-compose.yml and on the command line.

## Examples

**Fockerfile**

```yaml
base: freebsd-latest

fenv:
  PHP_VERSION: php74

steps:
  run:
    - export ASSUME_ALWAYS_YES=yes IGNORE_OSVERSION=yes
    - pkg install ${{ PHP_VERSION }}
    - pkg install ${{ PHP_VERSION }}-json
    - pkg install ${{ PHP_VERSION }}-mbstring
```

Then, on the command line:

`focker image build . --fenv PHP_VERSION php73`

to change php from the default `php74` to `php73`.

**Image in a composition**

Using the same `Fockerfile` as above, one could create a `focker-compose.yml` like this:

```yaml
images:
  foobar: .

fenv:
  PHP_VERSION: php73
```

to similarly override the `PHP_VERSION` variable. It can be overriden yet again on the command line:

`focker compose build ./focker-compose.yml --fenv PHP_VERSION php74`

bringing it back to `php74.`

**Volume in a composition**

Consider the following `focker-compose.yml`:

```yaml
fenv:
  ZFS_QUOTA: 10g
  UID: 0
  GID: 80
  PERMS: 0o750
volumes:
  foobar:
    chown: ${{ UID }}:${{ GID }}
    chmod: ${{ PERMS }}
    zfs:
      quota: ${{ ZFS_QUOTA }}
```

The `chown`, `chmod` and `zfs quota` parameters are now controlled by FEnv variables with default values of `0:80`, `0750` and `10g` respectively. **Note**: Please note that FEnv defaults are converted to strings and then parsed backed to the required type depending on the place they appear in.

These can be overriden on the command line in the following manner:

`focker compose build ./focker-compose.yml --fenv UID 80 GID 65533 PERMS 0o700 ZFS_QUOTA 5g`

**Jail in a composition**

Consider the following `focker-compose.yml`:

```yaml
fenv:
  IP4_ADDR: 127.0.55.1
  EXEC_FIB: 1
  SITE_NAME: foobar
  JAIL_USER: www
jails:
  foobar:
    image: foobar
    ip4.addr: ${{ IP4_ADDR }}
    exec.fib: ${{ EXEC_FIB }}
    env:
      SITE_NAME: ${{ SITE_NAME }}
    exec.jail_user: ${{ JAIL_USER }}
```

The `ip4.addr`, `exec.fib` and `exec.jail_user` parameters, as well as the `SITE_NAME` *regular* environment variable are controlled by respective *FEnv* variables with default values of `127.0.55.1`, `1`, `www` and `foobar`. **Note**: Please note that FEnv defaults are converted to strings and then parsed backed to the required type depending on the place they appear in.

The FEnv variables can now be overriden on the command line like this:

`focker compose build ./focker-compose.yml --fenv IP4_ADDR 127.0.33.1 EXEC_FIB 2 SITE_NAME bafbaz JAIL_USER nobody`

## Escaping FEnv substitution

As demonstrated above, FEnv variables use a dollar sign followed by double curly braces syntax of the form `${{ VARIABLE_NAME }}`. Variable names can consist of upper- and lowercase letters, digits and the underscore symbol. In order to escape this syntax (i.e. not invoke the substitution), one must express it as follows: `${{ '${{ VARIABLE_NAME }}' }}` - in other words, type the desired text which won't be subject to substitution in-between single- or double-quotes inside of a block surrounded by double curly braces and starting with a dollar sign.
