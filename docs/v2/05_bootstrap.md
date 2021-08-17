# Bootstrap

The built-in Focker 2.0 commands are mostly compatible with their 1.0 counterparts apart from `focker bootstrap`. It is now much more granular with different aspects of the bootstrap available as separate sub-commands rather than switches.

Importantly, Focker 2.0 does away with automatic creation of ZFS filesystems required for its function, so as not to perform any actions not explicitly requested by the user. This functionality now has also been moved to the `focker bootstrap` command.

Below, a quick list of steps necessary to get Focker running on a new system while using the default values for all parameters.

```sh
focker bootstrap filesystem
focker bootstrap interface
focker bootstrap pfrule
focker bootstrap install [-i]
# here one can customise the image
focker bootstrap finalize freebsd-latest
```

This will create the necessary ZFS datasets under zroot/focker mounted at /focker, create a lo1 interface for jails, add the corrsponding pf rule, create a base image with the FreeBSD version of the host and finalize the image so that it can be used by other images and jails.

Optionally, one can run the `focker bootstrap install` with the `-i` switch which will run the installer in interactive mode. Furthermore, the image can be manually customized before calling `focker bootstrap finalize`.
