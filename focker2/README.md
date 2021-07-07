# Focker 2

<font color=red>This version is not ready for any kind of use. Best not to touch it before the official availability announcement. It is being developed directly in this branch just for convenience.</font>

Focker is currently undergoing a slow overhaul which will eventually result
in version 2.0. The aim of this is to make the code more structured, have
better abstractions where possible and more reusability. In addition to that, two major things are in focus:

- Plugins system - the native Focker command modules (image, jail, compose) will become plugins themselves and the goal will be to implement every new block of functionality as a plugin on top of a slim and robust core,
- Configurability - at the same time the way Focker's configuration is passed around will be remade, allowing to pass any and all Focker parameters either on the command line OR via environmental variables OR by system/user-specific configuration files - /etc/focker.conf, ~/focker.conf,

and some smaller fixes:

- Taking into account the exec.fib setting when running focker jail exec,
- Automatically create mount destinations if they don't exist
- Allow for bootstrapping images using different versions of FreeBSD not only the current one,
- Allow to include other Fockerfiles inside of a Fockerfile, as an alternative to base image system,
- Make a few more settings configurable, e.g. whether to copy /etc/resolv.conf or not, possibility of static resolv.conf, etc.

Stay tuned.
