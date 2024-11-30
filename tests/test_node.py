import pytest
import sys
import os
import yaml

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

@pytest.fixture
def test_config():
    config_data = {
        "node": {
            "type": "coordinator",
            "id": "test-node",
            "host": "localhost",
            "port": 5000
        }
    }
    config_path = "test_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    yield config_path
    os.remove(config_path)


def test_config_loading(test_config):
    from eon.utils.config import Config
    config = Config(test_config)
    assert config.get("node.type") == "coordinator"

    
    # tests/test_node.py
def test_base_imports():
    from eon.core.node import manager, compute, coordinator, client
    assert manager is not None
    assert compute is not None
    assert coordinator is not None
    assert client is not None

def test_client():
    from eon.core.node.client import ComputationClient
    assert ComputationClient is not None