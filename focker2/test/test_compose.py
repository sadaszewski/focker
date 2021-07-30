from focker.__main__ import main
from focker.core import Volume
from focker import yaml
import os
import tempfile


class TestCompose:
    def test00_volume_simple(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        fnam = f.name
        f.close()
        with open(fnam, 'w') as f:
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
