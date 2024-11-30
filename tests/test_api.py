
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

def test_api_basic():
    from eon.api.schemas.computation import ComputationRequest
    assert ComputationRequest is not None




    # tests/test_api.py
def test_api_models():
    from eon.api.schemas.computation import ComputationRequest
    request = ComputationRequest(
        data_id="test",
        operation="add",
        params={"value": 1}
    )
    assert request.data_id == "test"