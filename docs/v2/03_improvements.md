# Other improvements in Focker 2.0

## Taking into account the exec.fib setting when running focker jail exec

Certain use cases as described e.g. [here](https://forums.freebsd.org/threads/example-setup-for-email-behind-vps-vpn-dsl-originally-a-nat-loopback-problem.81087/) require the usage of FreeBSD's alternative forwarding information base (FIB) mechanism. For processes executed through a jail's _exec.*_ family parameters, it suffices to specify the _exec.fib_ parameter. However, _jexec_ does not honor this setting automatically and requires to be wrapped in a call to [_setfib_](https://www.freebsd.org/cgi/man.cgi?query=setfib&sektion=2&format=html). Invocations of `focker jail exec` and similar now take this into account. 

## Support bootstrapping of images using different versions of FreeBSD than the host one

Certain images might be based on a set of packages with frozen versions (e.g. for reproducibility of scientific experiments). To this end, in case such images need to be rebuilt, it is useful to have the ability to bootstrap base images using an earlier version of FreeBSD. Using the new functionality by invoking e.g. `focker bootstrap install -v 11.4-RELEASE` one would create a base image using FreeBSD 11.4.

## Sorting of listing results and customizable listing columns

The `list` command for images, volumes and jails is now standardized and features a `--sort` parameter which can take one of the following values: `name`, `tags`, `sha256`, `mountpoint`, `is_protected`, `is_finalized` or `size`. The same values can be used to specify the columns in the listing using the `--output` parameter.

## Detect usage of volumes by jails when pruning

When running `focker volume prune` untagged volumes will not be removed if they are in use by a jail.

## Roundtrip jail.conf parser

Usage of leforestier's [jailconf](https://github.com/leforestier/jailconf) has been dropped in favor of my [custom](../../focker/jailconf) jail.conf parser. It is a round-trip parser which means that it preserves almost everything as-is when loading and saving back the file. This is in contrast to the prior situation when comments were stripped from **/etc/jail.conf** every time Focker rewrote it. The new parser is also easier to use and automatically manages quoting of values. It is the best jail.conf parser I know of, apart from the original thing in FreeBSD.

## Automatically create mount destinations if they don't exist

This is useful to avoid all the mkdirs in the Fockerfile. It will also save you from rebuilding an image if you forget them.

## Allow to include other Fockerfiles inside of a Fockerfile, as an alternative to the scheme of base images

Focker 2.0 introduces a mechanism which I call "facets". It allows to group different aspects of an image in separate files and combine them in the `Fockerfile` under the `facets` key. To learn more about this and other improvements in image building, see [Facets](./04_facets.md).

## Make it a setting whether to copy /etc/resolv.conf or not and/or specify a predefined resolv.conf

Focker jails now support a new parameter - _resolv_conf_ which can take the following values: _system_, _image_, _file_ or _system_file_. The _system_ setting corresponds to the Focker 1 behavior of copying the host resolv.conf file. _image_ instructs Focker to use the **/etc/resolv.conf** as provided by the image. The _file_ setting copies a file from a defined location **in the jail** to the jail's **/etc/resolv.conf**, whereas _system_file_ does the same using a location **on the host**.
