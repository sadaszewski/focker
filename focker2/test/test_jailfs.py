from dataset_test_base import DatasetTestBase
from dataset_cmd_test_base import DatasetCmdTestBase
from focker.core import JailFs, \
    CloneImageJailSpec, \
    OSJailSpec, \
    OSJail
from focker.__main__ import main
from contextlib import redirect_stdout
import io


class TestJailFs(DatasetTestBase):
    _meta_class = JailFs


class TestJailFsCmd(DatasetCmdTestBase):
    _meta_class = JailFs


class TestJailCmd:
    def test01_exec(self):
        spec = CloneImageJailSpec.from_dict({ 'image': 'freebsd-latest' })
        try:
            spec.jfs.add_tags([ 'focker-unit-test-jail' ])
            ospec = OSJailSpec.from_jailspec(spec)
            jail = ospec.add()
            jail.start()
            cmd = [ 'jail', 'exec', '-c', 'focker-unit-test-jail', '--', '/bin/sh', '-c', 'echo "foo bar baf"' ]
            buf = io.StringIO()
            with redirect_stdout(buf):
                main(cmd)
            assert 'foo bar baf' in buf.getvalue()
        finally:
            spec.jfs.destroy()

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
