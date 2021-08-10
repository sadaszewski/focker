from focker.misc import load_overrides
from common import _read_file_if_exists
import os
import focker.yaml as yaml
from tempfile import NamedTemporaryFile
import pytest


class TestOverrides:
    def test01_from_file(self):
        os.makedirs('/etc/focker', exist_ok=True)
        with NamedTemporaryFile(dir='/etc/focker') as f:
            # print('f.name:', f.name)
            yaml.safe_dump({ 'foo': 'bar' }, f)
            f.flush()
            _, name = os.path.split(f.name)
            over = load_overrides(name)
            assert 'foo' in over
            assert over['foo'] == 'bar'

    def test02_from_env(self):
        os.makedirs('/etc/focker', exist_ok=True)
        with NamedTemporaryFile(dir='/etc/focker') as f:
            os.environ['FOCKER_FOO'] = 'bar'
            try:
                _, name = os.path.split(f.name)
                over = load_overrides(name)
                assert 'foo' in over
                assert over['foo'] == 'bar'
            finally:
                del os.environ['FOCKER_FOO']

    def test03_from_env_hier(self):
        os.makedirs('/etc/focker', exist_ok=True)
        with NamedTemporaryFile(dir='/etc/focker') as f:
            os.environ['FOCKER_BAR_BAF_FOO'] = 'baz'
            try:
                _, name = os.path.split(f.name)
                over = load_overrides(name, env_hier=True)
                assert 'bar' in over
                assert 'baf' in over['bar']
                assert 'foo' in over['bar']['baf']
                assert over['bar']['baf']['foo'] == 'baz'
            finally:
                del os.environ['FOCKER_BAR_BAF_FOO']

    def test04_env_hier_conflict(self):
        os.makedirs('/etc/focker', exist_ok=True)
        with NamedTemporaryFile(dir='/etc/focker') as f:
            os.environ['FOCKER_BAZ'] = 'lorem'
            os.environ['FOCKER_BAZ_BAF_FOO'] = 'bar'
            try:
                _, name = os.path.split(f.name)
                with pytest.raises(TypeError, match='Expected dictionary'):
                    _ = load_overrides(name, env_hier=True)
            finally:
                del os.environ['FOCKER_BAZ']
                del os.environ['FOCKER_BAZ_BAF_FOO']
