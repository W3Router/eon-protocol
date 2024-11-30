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
        },
        "fhe": {
            "scheme": "CKKS",
            "poly_modulus_degree": 8192,
            "coeff_mod_bit_sizes": [60, 40, 40, 60]
        }
    }
    config_path = "test_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    yield config_path
    os.remove(config_path)

def test_node_manager(test_config):
    from eon.utils.config import Config
    from eon.core.node.manager import NodeManager
    config = Config(test_config)
    manager = NodeManager(config)
    assert manager is not None


        # tests/test_basic.py
def test_node_compute(test_config):
    from eon.utils.config import Config
    from eon.core.node.compute import ComputeNode
    from eon.core.proto import computation_pb2
    
    config = Config(test_config)
    try:
        node = ComputeNode(config)
        
        # 测试提交计算
        request = computation_pb2.ComputationRequest(
            data_id="test-data",
            operation="add"
        )
        response = node.SubmitComputation(request, None)
        assert response.status == "submitted"
        
        assert node is not None
    except Exception as e:
        pytest.fail(f"Failed to create ComputeNode: {str(e)}")