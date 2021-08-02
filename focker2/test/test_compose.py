from focker.__main__ import main
from focker.core import Volume, \
    JailFs, \
    OSJail
from focker import yaml
import os
import tempfile
import stat


class TestCompose:
    def test00_volume_simple(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            yaml.safe_dump(dict(
                volumes=dict(
                    focker_unit_test_volume=dict()
                )
            ), f)
        try:
            cmd = [ 'compose', 'build', f.name ]
            main(cmd)
            assert Volume.exists_tag('focker_unit_test_volume')
            v = Volume.from_tag('focker_unit_test_volume')
            v.destroy()
        finally:
            os.unlink(f.name)

    def test01_volume_params(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            yaml.safe_dump(dict(
                volumes=dict(
                    focker_unit_test_volume=dict(
                        chown='65534:65534',
                        chmod=0o123,
                        zfs={'focker:unit_test': 'on'},
                        protect=True
                    )
                )
            ), f)
        try:
            cmd = [ 'compose', 'build', f.name ]
            main(cmd)
            assert Volume.exists_tag('focker_unit_test_volume')
            v = Volume.from_tag('focker_unit_test_volume')
            try:
                st = os.stat(v.path)
                assert st.st_uid == 65534
                assert st.st_gid == 65534
                assert stat.S_IMODE(st.st_mode) == 0o123
                props = v.get_props([ 'focker:unit_test' ])
                assert props['focker:unit_test'] == 'on'
                assert v.is_protected
            finally:
                v.unprotect()
                v.destroy()
        finally:
            os.unlink(f.name)

    def test03_jail_simple(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            yaml.safe_dump(dict(
                jails=dict(
                    focker_unit_test_jail=dict(
                        image='freebsd-latest'
                    )
                )
            ), f)
        try:
            cmd = [ 'compose', 'build', f.name ]
            main(cmd)
            jfs = JailFs.from_tag('focker_unit_test_jail', raise_exc=False)
            assert jfs is not None
            try:
                jail = OSJail.from_tag('focker_unit_test_jail', raise_exc=False)
                assert jail is not None
                assert jail.conf['path'] == jfs.path
            finally:
                jfs.destroy()
            assert not JailFs.exists_tag('focker_unit_test_jail')
        finally:
            os.unlink(f.name)
