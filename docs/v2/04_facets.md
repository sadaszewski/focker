## Facets

With Focker 2.0 you can for example use the following layout in your Focker directory:

```
facets/
  01_nginx.yml
  02_php.yml
  03_php-fpm.yml
Fockerfile
```

And construct your Fockerfile like this:
```
base: freebsd-latest

facets:
  - ./facets/01_nginx.yml
  - ./facets/02_php.yml
  - ./facets/03_php-fpm.yml
```

where 01_nginx.yml:
```
steps:
  - run:
    - export IGNORE_OSVERSION=yes ASSUME_ALWAYS_YES=yes
    - pkg install nginx
    - service enable nginx
```

02_php.yml:
```
steps:
  - run:
    - export IGNORE_OSVERSION=yes ASSUME_ALWAYS_YES=yes
    - pkg install php70
```

03_php-fpm.yml:
```
steps:
  - run:
    - export IGNORE_OSVERSION=yes ASSUME_ALWAYS_YES=yes
    - pkg install php-fpm
    - service enable php-fpm
```

The steps from the respective facets will be concatenated and the effect of building such an image will be the same as if they were contained in the single Fockerfile from the beginning. This just improves the organization of the image building code without requiring you to (ab)use the mechanism of base images.

## Dictionary-based steps

In addition to _facets_, Focker 2.0 introduces one more innovation to make image recipe development easier and faster - dictionary-based steps. Instead of using a list of steps, one can specify a dictionary, where keys can be of an arbitrary sortable type (usually strings or numbers), whereas values contain the old-fashioned lists of steps. In such a situation the lists of steps will be concatenated in the order determined by the order of the keys coming from the dictionaries. This mechanic works also across facets and allows to append commands in any place without the need to rebuild the image from scratch (or from an earlier snapshot). An example:

01_nginx.yml:
```
steps:
  4: # forgot to copy the nginx.conf file
    - copy:
      - [ files/nginx.conf, /usr/local/etc/nginx.conf ]
  1:
    - run:
      - export IGNORE_OSVERSION=yes ASSUME_ALWAYS_YES=yes
      - pkg install nginx
      - service enable nginx
```

02_php.yml:
```
steps:
  2:
    - run:
      - export IGNORE_OSVERSION=yes ASSUME_ALWAYS_YES=yes
      - pkg install php70
```

03_php-fpm.yml:
```
steps:
  3:
    - run:
      - export IGNORE_OSVERSION=yes ASSUME_ALWAYS_YES=yes
      - pkg install php-fpm
      - service enable php-fpm
```

**Note**: The type of steps specification must be consistent across facets - all facets must use the same, either dictionary-based or list-based steps.
