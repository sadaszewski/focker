# Focker 2

```diff
- IMPORTANT LEGAL NOTICE
- I oppose totalitarianism, anti-constitutional crimes and crimes against Human Rights.
- If you support forced or effectively forced gene therapy (or other medical
- procedures), please abstain from using this and any other software of mine.
```

To install Focker 2, please read the [Installation](./docs/v2/06_installation.md) manual.

For introduction, see [Basic Usage Guide](./docs/Basic_Usage_Guide.md) or [Detailed Intro](./docs/Detailed_Intro.md). For an end-to-end example with description, see the [scm-manager](./example/scm-manager/README.md) example.

Focker underwent a not-so-slow overhaul in the period of June-August 2021 which was concluded by the release of version 2.0. The aim was to make the code more structured, have better abstractions/more reusability and to lay foundations for the future development. Consequently, three major objectives have been achieved:

- [X] [API](./docs/v2/00_api.md) - new abstractions constitute a framework which makes Focker as easy to use in custom code as in the command line,
- [X] [Configurability](./docs/v2/01_config.md) - at the same time the way Focker's configuration is passed around has been remade, allowing to pass any and all Focker parameters either on the command line OR via environment variables OR by system/user-specific configuration files - /etc/focker.conf, /usr/local/etc/focker.conf and ~/focker.conf,
- [X] [Plugins](./docs/v2/02_plugins.md) system - the native Focker command modules (image, jail, compose) have become plugins themselves and the rule now is to implement every new block of functionality as a plugin on top of the slim and robust core.

Three important mechanisms have changed:
- [X] [Facets](./docs/v2/04_facets.md) - _facets_ and _dictionary-based steps_ are innovations that vastly improve the image recipe writing experience,
- [X] [FEnv](./docs/v2/07_focker_env.md) (Focker Environment) Variables can be used to parametrize the processes of image and composition building.
- [X] [Bootstrap](./docs/v2/05_bootstrap.md) - bootstrap is now more granular and gives user more control.

Focker 2.0 introduced as well many smaller [Improvements](./docs/v2/03_improvements.md):
- [X] Taking into account the exec.fib setting when running focker jail exec,
- [X] Allow for bootstrapping images using different versions of FreeBSD not only the current one,
- [X] Sorting of listing results,
- [X] Configurable prefix for names in /etc/jail.conf,
- [X] Configurable location (dataset) for focker objects.
- [X] Detect usage of volumes by jails when pruning
- [X] Roundtrip jail.conf parser
- [X] Automatically create mount destinations if they don't exist
- [X] Allow to include other Fockerfiles inside of a Fockerfile, as an alternative to the scheme of base images,
- [X] Make a few more settings configurable, e.g. whether to copy /etc/resolv.conf or not, possibility of static resolv.conf, etc.,

Future development will focus on providing the "Infrastructure as Code" functionality well-known from the Kubernetes (K8s) ecosystem and highly appreciated by the industry.
