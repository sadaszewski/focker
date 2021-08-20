from dataset_test_base import DatasetTestBase
from dataset_cmd_test_base import DatasetCmdTestBase
from focker.core import JailFs, \
    clone_image_jailspec, \
    OSJailSpec, \
    OSJail
from focker.__main__ import main
from contextlib import redirect_stdout, \
    ExitStack
import io
from tempfile import TemporaryDirectory
import os


class TestJailFs(DatasetTestBase):
    _meta_class = JailFs


class TestJailFsCmd(DatasetCmdTestBase):
    _meta_class = JailFs


class TestJailCmd:
    def test01_exec(self):
        with clone_image_jailspec({ 'image': 'freebsd-latest' }) as (spec, jfs, _):
            jfs.add_tags([ 'focker-unit-test-jail' ])
            ospec = OSJailSpec.from_jailspec(spec)
            jail = ospec.add()
            jail.start()
            cmd = [ 'jail', 'exec', '-c', 'focker-unit-test-jail', '--', '/bin/sh', '-c', 'echo "foo bar baf"' ]
            buf = io.StringIO()
            with redirect_stdout(buf):
                main(cmd)
            assert 'foo bar baf' in buf.getvalue()

    def test02_oneexec(self):
        cmd = [ 'jail', 'oneexec', '-c', 'freebsd-latest', '--', '/bin/sh', '-c', 'echo "foo bar baf"' ]
        buf = io.StringIO()
        with redirect_stdout(buf):
            main(cmd)
        assert 'foo bar baf' in buf.getvalue()

    def test03_fromimage(self):
        cmd = [ 'jail', 'fromimage', '-t', 'focker-unit-test-jail', '--', 'freebsd-latest', 'exec.fib=1234' ]
        print('cmd:', cmd)
        main(cmd)
        assert JailFs.exists_tag('focker-unit-test-jail')
        jfs = JailFs.from_tag('focker-unit-test-jail')
        try:
            jail = OSJail.from_mountpoint(jfs.path)
            conf = jail.conf
            assert 'exec.fib' in conf
            assert conf['exec.fib'] == 1234
        finally:
            jfs.destroy()

    def test04_with_mounts(self):
        with TemporaryDirectory() as d:
            # print('d:', d)
            with open(os.path.join(d, '.focker-unit-test-jail'), 'w') as f:
                f.write('foobar\n')
            with clone_image_jailspec({ 'image': 'freebsd-latest', 'mounts': { d: '/mnt' } }) as (spec, jfs, _):
                ospec = OSJailSpec.from_jailspec(spec)
                jail = ospec.add()
                jail.start()
                fname = os.path.join(jfs.path, 'mnt/.focker-unit-test-jail')
                assert os.path.exists(fname)
                with open(fname) as f:
                    data = f.read()
                assert data.strip() == 'foobar'

    def test05_exec_no_chkout(self):
        with clone_image_jailspec({ 'image': 'freebsd-latest' }) as (spec, jfs, _):
            jfs.add_tags([ 'focker-unit-test-jail' ])
            ospec = OSJailSpec.from_jailspec(spec)
            jail = ospec.add()
            jail.start()
            cmd = [ 'jail', 'exec', 'focker-unit-test-jail', '--', '/bin/sh', '-c', 'touch /.focker-unit-test-jail' ]
            main(cmd)
            assert os.path.exists(os.path.join(jfs.path, '.focker-unit-test-jail'))

    def test06_jid(self):
        with clone_image_jailspec({ 'image': 'freebsd-latest' }) as (spec, jfs, _):
            ospec = OSJailSpec.from_jailspec(spec)
            jail = ospec.add()
            jail.start()
            assert jail.jid is not None
            assert jfs.jid is not None
            assert jail.jid == jfs.jid
