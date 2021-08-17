# Other improvements in Focker 2.0

## Taking into account the exec.fib setting when running focker jail exec

Certain use cases as described e.g. [here](https://forums.freebsd.org/threads/example-setup-for-email-behind-vps-vpn-dsl-originally-a-nat-loopback-problem.81087/) require usage of FreeBSD's alternative forwarding information base (FIB) mechanism. For processes executed via a jail's _exec.*_ family parameters it suffices to specify the _exec.fib_ parameter. However _jexec_ does not honor this setting automatically and requires to be wrapped in a call to [_setfib_](https://www.freebsd.org/cgi/man.cgi?query=setfib&sektion=2&format=html). Invocations of `focker jail exec` and similar will now take this into account. 

## Allow for bootstrapping images using different versions of FreeBSD not only the current one,

## Sorting of listing results,

## Configurable prefix for names in /etc/jail.conf,

## Configurable location (dataset) for focker objects.

## Detect usage of volumes by jails when pruning

## Roundtrip jail.conf parser

## Automatically create mount destinations if they don't exist

## Allow to include other Fockerfiles inside of a Fockerfile, as an alternative to the scheme of base images,

## Make a few more settings configurable, e.g. whether to copy /etc/resolv.conf or not, possibility of static resolv.conf, etc.,
