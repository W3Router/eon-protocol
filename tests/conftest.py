# tests/conftest.py
import pytest
import yaml
import os

@pytest.fixture
def test_config():
    config_data = {
        "node": {
            "type": "compute",
            "id": "test-node",
            "host": "localhost",
            "port": 50051
        },
        "fhe": {
            "scheme": "CKKS",
            "poly_modulus_degree": 8192,
            "coeff_mod_bit_sizes": [60, 40, 40, 60]
        },
        "grpc": {
            "max_workers": 2
        },
        "storage": {
            "type": "memory"
        },
        "logging": {
            "level": "INFO",
            "format": "json"
        }
    }
    config_path = "test_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    yield config_path
    os.remove(config_path)