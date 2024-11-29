
import pytest
import numpy as np
from eon.core.fhe.engine import FHEEngine

@pytest.fixture
def fhe_engine():
    """创建FHE引擎实例"""
    config = {
        'poly_modulus_degree': 8192,
        'coeff_mod_bit_sizes': [60, 40, 40, 60],
        'scale': 40
    }
    return FHEEngine(config)

def test_encrypt_decrypt():
    """测试加密解密"""
    engine = fhe_engine()
    data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    
    # 加密数据
    encrypted = engine.encrypt(data)
    assert encrypted is not None
    
    # 解密数据
    decrypted = engine.decrypt(encrypted)
    np.testing.assert_array_almost_equal(data, decrypted, decimal=4)

def test_homomorphic_operations():
    """测试同态运算"""
    engine = fhe_engine()
    data = np.array([1.0, 2.0, 3.0])
    
    # 加密数据
    encrypted = engine.encrypt(data)
    
    # 测试加法
    result = engine.compute(encrypted, "add", {"value": 1.0})
    decrypted = engine.decrypt(result)
    np.testing.assert_array_almost_equal(data + 1.0, decrypted, decimal=4)
    
    # 测试乘法
    result = engine.compute(encrypted, "multiply", {"value": 2.0})
    decrypted = engine.decrypt(result)
    np.testing.assert_array_almost_equal(data * 2.0, decrypted, decimal=4)

def test_invalid_operations():
    """测试无效操作"""
    engine = fhe_engine()
    data = np.array([1.0, 2.0, 3.0])
    encrypted = engine.encrypt(data)
    
    with pytest.raises(ValueError):
        engine.compute(encrypted, "invalid_op", {})

def test_batch_processing():
    """测试批量处理"""
    engine = fhe_engine()
    data = np.random.rand(1000)
    
    # 加密大量数据
    encrypted = engine.encrypt(data)
    assert encrypted is not None
    
    # 计算平均值
    result = engine.compute(encrypted, "mean")
    decrypted = engine.decrypt(result)
    np.testing.assert_almost_equal(np.mean(data), decrypted, decimal=4)
