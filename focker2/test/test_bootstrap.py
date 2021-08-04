from focker.__main__ import main
import os
from focker.core import Image


def _read_file_if_exists(fname, default=None):
    if os.path.exists(fname):
        with open(fname, 'r') as f:
            return f.read()

    return default


class TestBootstrap:
    def test01_pfrule(self):
        old = _read_file_if_exists('/etc/pf.conf', '')
        try:
            cmd = [ 'bootstrap', 'pfrule' ]
            main(cmd)
            with open('/etc/pf.conf', 'r') as f:
                new = f.read()
            assert new[len(old):].startswith('\n##### Rule added by Focker #####\n')
        finally:
            with open('/etc/pf.conf', 'w') as f:
                f.write(old)

    def test02_iface(self):
        cmd = [ 'bootstrap', 'iface' ]
        old = _read_file_if_exists('/etc/rc.conf', '')
        try:
            main(cmd)
            new = _read_file_if_exists('/etc/rc.conf', '')
            new = new.split('\n')
            new = [ ln for ln in new if ln.startswith('cloned_interfaces=') and 'tun0' in ln ]
            assert len(new) == 1
        finally:
            with open('/etc/rc.conf', 'w') as f:
                f.write(old)

    def test03_install(self):
        cmd = [ 'bootstrap', 'install', '-t', 'focker-unit-test-install' ]
        main(cmd)
        assert Image.exists_tag('focker-unit-test-install')
        im = Image.from_tag('focker-unit-test-install')
        im.destroy()

    def test04_install_version(self):
        cmd = [ 'bootstrap', 'install', '-t', 'focker-unit-test-install', '-v', '13.0-RELEASE' ]
        main(cmd)
        assert Image.exists_tag('focker-unit-test-install')
        im = Image.from_tag('focker-unit-test-install')
        im.destroy()

    def test05_install_version_cleandist(self):
        cmd = [ 'bootstrap', 'install', '-t', 'focker-unit-test-install', '-v', '13.0-RELEASE', '-c' ]
        main(cmd)
        assert Image.exists_tag('focker-unit-test-install')
        im = Image.from_tag('focker-unit-test-install')
        im.destroy()
        assert not os.path.exists('/usr/freebsd-dist-13.0-RELEASE')
