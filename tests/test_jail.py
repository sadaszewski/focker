from focker.jail import backup_file
import tempfile
import os


def test_backup_file():
    with tempfile.TemporaryDirectory() as d:
        fname = os.path.join(d, 'dummy.conf')
        with open(fname, 'w') as f:
            f.write('init')
        nbackups = 10
        for i in range(15):
            backup_file(fname, nbackups=nbackups, chmod=0o640)
            with open(fname, 'w') as f:
                f.write(str(i))

        fname = os.path.join(d, 'dummy.conf')
        with open(fname, 'r') as f:
            assert f.read() == '14'

        for i in range(nbackups):
            fname = os.path.join(d, 'dummy.conf.%d' % i)
            assert os.path.exists(fname)
            with open(fname, 'r') as f:
                if i < 5:
                    assert f.read() == str(i + 9)
                else:
                    assert f.read() == str(i - 1)
