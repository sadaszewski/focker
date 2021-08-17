# Configuration

In Focker 2 many more things are configurable and the number of ways to specify them has increased.

The 3 ways to provide configuration values to Focker are (in order of increasing priority):

1. Configuration files
2. Environment variables
3. Command-line parameters

## Configuration files

Configuration files are all YAML-based and come in three flavors:

- **focker.conf** specifies the 3 parameters fundamental for Focker operation - _root_dataset_, _root_mountpoint_ and _jail_name_prefix_. They define respectively the name of the ZFS dataset which serves as the Focker "root", the path in the directory hierarchy where the "root" dataset is mounted and finally the prefix that is used for Focker-managed jails in the **/etc/jail.conf** file.
- **jail-defaults.conf** overrides the default parameters of jails managed by Focker. The built-in defaults can be found at [focker/core/config/jail.py:13](../../focker/core/config/jail.py#L13). **jail-defaults.conf** must provide a dictionary which will be merged with the _DEFAULT_PARAMS_ constant.
- **command.conf** can override the default values of command-line parameters for all the parsers and subparsers used by Focker. It contains a hierarchical dictionary where subsequent nested keys specify the first and second sub-command and the parameter name. The values specify the new defaults for the corresponding parameters, e.g. `{ 'jail': { 'list': { 'sort': 'tags' } } }`.

Configuration files are searched always in the same order in the following locations: **~/.focker**, **/usr/local/etc/focker** and **/etc/focker**. Only the first file found is used so that the user-specific configuration has complete precedence over system-wide configuration.

## Environment Variables

Environment variables take priority over parameters specified in the configuration files. Each config file has a specific environment variable prefix associated with it. These are:

- _FOCKER_CONF&lowbar;_ for the **focker.conf** file
- _FOCKER_JAIL_DEFAULTS&lowbar;_ for the **jail-defaults.conf** file
- _FOCKER_CMD&lowbar;_ for the **command.conf** file

In the case of _FOCKER_CMD&lowbar;_ the underscores are also used to indicate the separation in levels of hierarchy, so that the example above would be denoted as `setenv FOCKER_CMD_JAIL_LIST_SORT tags ; focker jail list`.

Two more examples: `setenv FOCKER_CONF_ROOT_DATASET zroot/myfockerroot`, `setenv FOCKER_JAIL_DEFAULTS_IP4.ADDR 127.0.5.5`.

## Command-line parameters

### WiP
