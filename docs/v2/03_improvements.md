# Other improvements in Focker 2.0

## Taking into account the exec.fib setting when running focker jail exec

Certain use cases as described e.g. [here](https://forums.freebsd.org/threads/example-setup-for-email-behind-vps-vpn-dsl-originally-a-nat-loopback-problem.81087/) require the usage of FreeBSD's alternative forwarding information base (FIB) mechanism. For processes executed through a jail's _exec.*_ family parameters, it suffices to specify the _exec.fib_ parameter. However, _jexec_ does not honor this setting automatically and requires to be wrapped in a call to [_setfib_](https://www.freebsd.org/cgi/man.cgi?query=setfib&sektion=2&format=html). Invocations of `focker jail exec` and similar now take this into account. 

## Support bootstrapping of images using different versions of FreeBSD than the host one

Certain images might be based on a set of packages with frozen versions (e.g. for reproducibility of scientific experiments). To this end, in case such images need to be rebuilt, it is useful to have the ability to bootstrap base images using an earlier version of FreeBSD. Using the new functionality by invoking e.g. `focker bootstrap install -v 11.4-RELEASE` one would create a base image using FreeBSD 11.4.

## Sorting of listing results

## Configurable prefix for names in /etc/jail.conf,

## Configurable location (dataset) for focker objects.

## Detect usage of volumes by jails when pruning

## Roundtrip jail.conf parser

## Automatically create mount destinations if they don't exist

## Allow to include other Fockerfiles inside of a Fockerfile, as an alternative to the scheme of base images,

## Make a few more settings configurable, e.g. whether to copy /etc/resolv.conf or not, possibility of static resolv.conf, etc.,
