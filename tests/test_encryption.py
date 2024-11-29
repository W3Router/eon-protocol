# tests/test_encryption.py
import pytest
import sys
import os

# 添加源码目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

def test_tenseal_basic():
    try:
        import tenseal as ts
        context = ts.context(
            ts.SCHEME_TYPE.BFV,
            poly_modulus_degree=4096,
            plain_modulus=1024
        )
        assert context is not None
    except Exception as e:
        pytest.fail(f"Failed to create TenSEAL context: {e}")