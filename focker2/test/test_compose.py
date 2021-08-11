from focker.__main__ import main
from focker.core import Volume, \
    JailFs, \
    OSJail, \
    Image
from focker import yaml
import os
import tempfile
import stat
import pytest
from subprocess import CalledProcessError


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

    def _test_hook(self, hook_name='exec.prebuild'):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, 'focker-compose.yml'), 'w') as f:
                yaml.safe_dump({
                    hook_name: f'touch {os.path.join(d, f"focker-unit-test-{hook_name}.txt")}'
                }, f)
            cmd = [ 'compose', 'build', os.path.join(d, 'focker-compose.yml') ]
            main(cmd)
            assert os.path.exists(os.path.join(d, f'focker-unit-test-{hook_name}.txt'))

    def test04_prebuild(self):
        self._test_hook('exec.prebuild')

    def test05_postbuild(self):
        self._test_hook('exec.postbuild')

    def _test_hook_fail(self, hook_name='exec.prebuild'):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, 'focker-compose.yml'), 'w') as f:
                yaml.safe_dump({
                    hook_name: f'rm {os.path.join(d, f"focker-unit-test-{hook_name}.txt")}'
                }, f)
            cmd = [ 'compose', 'build', os.path.join(d, 'focker-compose.yml') ]
            with pytest.raises(RuntimeError, match='failed'):
                main(cmd)

    def test06_prebuild_fail(self):
        self._test_hook_fail('exec.prebuild')

    def test07_postbuild_fail(self):
        self._test_hook_fail('exec.postbuild')

    def _test_hook_type_error(self, hook_name):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, 'focker-compose.yml'), 'w') as f:
                yaml.safe_dump({
                    hook_name: 1234567
                }, f)
            cmd = [ 'compose', 'build', os.path.join(d, 'focker-compose.yml') ]
            with pytest.raises(TypeError, match='string or a list of strings'):
                main(cmd)

    def test08_prebuild_type_error(self):
        self._test_hook_type_error('exec.prebuild')

    def test09_prebuild_type_error(self):
        self._test_hook_type_error('exec.postbuild')

    def test10_build_image(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, 'focker-compose.yml'), 'w') as f:
                yaml.safe_dump({
                    'images': { 'focker-unit-test-compose': '.' }
                }, f)
            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump({
                    'base': 'freebsd-latest',
                    'steps': [ { 'run': 'touch /.focker-unit-test-compose' } ]
                }, f)
            cmd = [ 'compose', 'build', os.path.join(d, 'focker-compose.yml') ]
            main(cmd)
            assert Image.exists_tag('focker-unit-test-compose')
            im = Image.from_tag('focker-unit-test-compose')
            im.destroy()
