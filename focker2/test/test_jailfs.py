from dataset_test_base import DatasetTestBase
from dataset_cmd_test_base import DatasetCmdTestBase
from focker.core import JailFs


class TestJailFs(DatasetTestBase):
    _meta_class = JailFs


class TestJailFsCmd(DatasetCmdTestBase):
    _meta_class = JailFs
