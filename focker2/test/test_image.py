from dataset_test_base import DatasetTestBase
from dataset_cmd_test_base import DatasetCmdTestBase
from focker.core import Image
import focker.yaml as yaml
from focker.__main__ import main
from tempfile import TemporaryDirectory
import os


class TestImage(DatasetTestBase):
    _meta_class = Image


class TestImageCmd(DatasetCmdTestBase):
    _meta_class = Image

    def test14_build(self):
        with TemporaryDirectory() as d:
            with open(os.path.join(d, 'Fockerfile'), 'w') as f:
                yaml.safe_dump(dict(
                    base='freebsd-latest',
                    steps=[
                        dict(run=[
                            'touch /.focker-unit-test'
                        ])
                    ]
                ), f)
            cmd = [ 'image', 'build', d, '-t', 'focker-unit-test-image' ]
            main(cmd)
            assert Image.exists_tag('focker-unit-test-image')
            im = Image.from_tag('focker-unit-test-image')
            assert os.path.exists(os.path.join(im.path, '.focker-unit-test'))
            im.destroy()
