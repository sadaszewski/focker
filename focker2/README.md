# Focker 2

```diff
- This version is not ready
- for any kind of use.
- Best not to touch it before
- the official availability
- announcement. It is kept
- in this branch for convenience.
```

Focker is currently undergoing a slow overhaul which will eventually result
in version 2.0. The aim of this is to make the code more structured, have
better abstractions where possible and more reusability. Consequently, three major things are in focus:

- [X] API - new abstractions constitute a framework which makes Focker as easy to use in custom code as in the command line,
- [X] Configurability - at the same time the way Focker's configuration is passed around will be remade, allowing to pass any and all Focker parameters either on the command line OR via environmental variables OR by system/user-specific configuration files - /etc/focker.conf, ~/focker.conf,
- [ ] Plugins system - the native Focker command modules (image, jail, compose) will become plugins themselves and the goal will be to implement every new block of functionality as a plugin on top of a slim and robust core,

and some smaller fixes:

- [X] Taking into account the exec.fib setting when running focker jail exec,
- [X] Allow for bootstrapping images using different versions of FreeBSD not only the current one,
- [X] Sorting of listing results,
- [X] Configurable prefix for names in /etc/jail.conf,
- [X] Configurable location (dataset) for focker objects.
- [X] Detect usage of volumes by jails when pruning (maybe)
- [X] Roundtrip jail.conf parser
- [X] Automatically create mount destinations if they don't exist
- [ ] Allow to include other Fockerfiles inside of a Fockerfile, as an alternative to the scheme of base images,
- [ ] Make a few more settings configurable, e.g. whether to copy /etc/resolv.conf or not, possibility of static resolv.conf, etc.,
- [ ] Mount volumes while building images

Stay tuned.
