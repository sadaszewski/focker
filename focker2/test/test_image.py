from dataset_test_base import DatasetTestBase
from dataset_cmd_test_base import DatasetCmdTestBase
from focker.core import Image


class TestImage(DatasetTestBase):
    _meta_class = Image


class TestImageCmd(DatasetCmdTestBase):
    _meta_class = Image
