from dataset_test_base import DatasetTestBase
from dataset_cmd_test_base import DatasetCmdTestBase
from focker.core import Volume


class TestVolume(DatasetTestBase):
    _meta_class = Volume


class TestVolumeCmd(DatasetCmdTestBase):
    _meta_class = Volume
