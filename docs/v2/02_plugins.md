# Plugins

Plugins were an essentially unused feature of Focker 1 and one that arrived very late - just prior to starting the work on Focker 2. Plugins in Focker 2 are quite different in a number of ways but most importantly the built-in functionality of the CLI is now provided by means of the plugins mechanism. Namely, every top level command (_jail_, _image_, _volume_, _bootstrap_, _compose_) along with all its subcommands is provided by a separate plugin. Thanks to this approach, the framework will undoubtedly stay fully functional whether 3rd party plugins start arriving sooner or later.

## Plugin detection

In order for a plugin to be detected by Focker it has to adhere to certain formal requirements:

- it must be a class descending from [_focker.plugin.Plugin_](../../focker/plugin.py).
- the name of the class must end with _Plugin_, e.g. _BootstrapPlugin_.
- it can be contained in an arbitrarily nested module but the top-level module/package name must start with _focker&lowbar;_

## Anatomy of a plugin

The _Plugin_ class currently defines 5 static methods, some of which should be overriden by the descendant class. These are:

- _provide_parsers()_
- _extend_parsers()_
- _change_defaults()_
- _install_pre_hooks()_
- _install_post_hooks()_

All methods share the same signature. They do not accept arguments and must return a dictionary. The meaning of the dictionary is different depending on the method.

The _provide_parsers()_ method should return definitions of one or more new parsers for the CLI provided by the plugin. Care must be taken not to cause collision with the built-in commands or other plugins. The content of the dictionary from the _provide_parsers()_ method will shallowly overwrite existing keys in the parser definition dictionary. For an example, please take a look at any of the built-in plugins, e.g. [_BootstrapPlugin_](../../focker/cmdmodule/bootstrap/bootstrap/bootstrap.py). The order in which the plugins are loaded is not defined, therefore it is not possible to make the overwriting behavior controlled - collisions must be currently avoided.

WiP
