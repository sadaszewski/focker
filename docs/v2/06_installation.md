# Installing Focker 2

First of all, you need to install Python, pip and git, e.g. like below:

```console
$ pkg install python3 py38-pip git
```

Then, you can use pip to install Focker directly from the Git repository like so:

```console
$ pip install git+https://github.com/sadaszewski/focker.git
```

Finally, if you are installing on a fresh FreeBSD system, you need to bootstrap Focker by invoking the following commands:

```console
$ focker bootstrap filesystem
$ focker bootstrap interface
$ focker bootstrap pfrule
$ service pf enable
$ service pf start
$ setenv MIRROR ftp://ftp.ch.freebsd.org
$ focker bootstrap install
$ focker bootstrap finalize freebsd-latest
```

The line containing `setenv MIRROR` should specify your FreeBSD mirror of choice. If you do not specify a mirror, a random one will be selected using the `focker-mirrorselect` script. Mirrors seem to come and go from release to release and the script is rarely updated, therefore if you do not manually specify a reliable mirror, the installation procedure might fail. In that case, `rm -rvf /usr/freebsd-dist` and try again with a different mirror.

The above uses the default settings for the Focker root dataset (`zroot/focker`), jail network interface (`lo1`) and jail IP address (`127.0.1.0`). It will also try to guess the external network interface by taking the first non-loopback name from a call to `ifconfig -l`. If you need to change those, please customize the `filesystem`, `interface` and `pfrule` invocations.

That's it. You can continue with the [Basic Usage Guide](../Basic_Usage_Guide.md) or [Detailed Intro](../Detailed_Intro.md). For an end-to-end example with description, see the [scm-manager](../../example/scm-manager/README.md) example.
