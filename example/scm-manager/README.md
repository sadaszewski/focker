# scm-manager setup using Focker

## Quickstart

From a fresh FreeBSD install to running scm-manager in a jail, you just need
to replace `em0` with the name of your external interface and make sure that
you are not using `lo1` for other purposes:

```bash
ASSUME_ALWAYS_YES=yes IGNORE_OSVERSION=yes pkg install git python3 py37-pip
git clone https://github.com/sadaszewski/focker.git
cd focker
python3 setup.py sdist
pip install dist/focker-0.95.tar.gz
focker bootstrap --non-interactive --create-interface
echo "rdr on em0 proto tcp from any to (em0) port 8080 -> 127.0.55.1 port 8080" >>/etc/pf.conf
echo "nat on em0 from (lo1:network) -> (em0)" >>/etc/pf.conf
sysrc pf_enable=YES
sysrc jail_enable=YES
service pf start
cd example/scm-manager
focker compose build ./focker-compose.yml
focker jail start scm-manager
```

Voila! scm-manager should now be available on port 8080 on your external
interface.

## Build file

The setup is based on the official instructions found
[here](https://www.scm-manager.org/docs/2.1.x/en/installation/unix/).

Since scm-manager seems to be a largely self-contained Java application,
the recipe is rather simple and consists of the following steps:

1. Installing openjdk11
2. Downloading scm-manager distribution archives
3. Extracting the archives to /opt
4. Cleanup of the image

The script looks like this:

```yaml
base: freebsd-latest

steps:
  - run: # Install OpenJDK 11
    - ASSUME_ALWAYS_YES=yes IGNORE_OSVERSION=yes pkg install openjdk11 ca_root_nss
  - run: # Startup script dependency: bash
    - ASSUME_ALWAYS_YES=yes IGNORE_OSVERSION=yes pkg install bash
  - run: # Startup script dependency: jsvc
    - fetch https://downloads.apache.org//commons/daemon/source/commons-daemon-1.2.2-src.tar.gz
    - tar -zvxf commons-daemon-1.2.2-src.tar.gz
    - cd /commons-daemon-1.2.2-src/src/native/unix
    - ./configure --with-java=/usr/local/openjdk11
    - make
    - mkdir -p /opt/scm-server/libexec
    - cp jsvc /opt/scm-server/libexec/jsvc-freebsd-amd64
    - rm -rvf /commons-daemon-1.2.2-src
    - rm -v /commons-daemon-1.2.2-src.tar.gz
  - run: # Optional dependencies: Mercurial
    - ASSUME_ALWAYS_YES=yes IGNORE_OSVERSION=yes pkg install mercurial
  - run: # Fetch scm-manager archives
    - fetch https://packages.scm-manager.org/repository/releases/sonia/scm/packaging/unix/2.1.0/unix-2.1.0-app.tar.gz
  - run: # Extract the archives to /opt
    - mkdir -p /opt
    - tar -zvxf unix-2.1.0-app.tar.gz -C /opt
  - run: # Clean package archives
    - rm -v unix-2.1.0-app.tar.gz
    - ASSUME_ALWAYS_YES=yes pkg clean --all
  - run: # Basic setup
    - sysrc sshd_enable=NO
    - sysrc sendmail_enable=NONE
    - sysrc clear_tmp_enable=YES
    - sysrc syslogd_flags="-ss"
    - chown root:wheel /var/spool/clientmqueue
    - chmod 000 /var/spool/clientmqueue
  - run: # Some fixes
    - ln -s /usr/local/bin/bash /bin/bash
    - echo "export JAVA_HOME=/usr/local/openjdk11" >>/.profile
  - run:
    - pw user mod nobody -d /scm-manager
    - mkdir -p /scm-manager/.scm
    - chown -R nobody:nobody /scm-manager
    - chown -R nobody:nobody /opt/scm-server
```

## Composition

The purpose of a composition will be to define a jail for scm-manager and
provide a volume which will store the persistent data and allow for easy
migration to a new machine in the future.

The file looks like this:

```yaml
images:
  scm-manager: .

volumes:
  scm-manager:
    chown: 65534:65534
    chmod: 0750

jails:
  scm-manager:
    image: scm-manager
    mounts:
      scm-manager: /scm-manager/.scm
    ip4.addr: 127.0.55.1
    exec.start: |
      JAVA_HOME=/usr/local/openjdk11 \
      HOME=/scm-manager \
        su -m nobody -c "/opt/scm-server/bin/scm-server start"
    exec.stop: |
      JAVA_HOME=/usr/local/openjdk11 \
      HOME=/scm-manager \
        su -m nobody -c "/opt/scm-server/bin/scm-server stop"
```
