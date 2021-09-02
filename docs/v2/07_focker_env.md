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
    - pkg install {{ PHP_VERSION }}
    - pkg install {{ PHP_VERSION }}-json
    - pkg install {{ PHP_VERSION }}-mbstring
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

```diff
-TODO
```

**Jail in a composition**

```diff
-TODO
```
