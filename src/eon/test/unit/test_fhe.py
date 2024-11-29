import pytest
import numpy as np
from eon.core.fhe.engine import FHEEngine

@pytest.fixture
def fhe_engine():
    """创建FHE引擎实例"""
    config = {
        "poly_modulus_degree": 8192,
        "coeff_mod_bit_sizes": [60, 40, 40, 60]
    }
    return FHEEngine(config)

def test_encrypt_decrypt(fhe_engine):
    """测试加密和解密功能"""
    # 准备测试数据
    original_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    
    # 加密数据
    encrypted_data = fhe_engine.encrypt(original_data)
    
    # 解密数据
    decrypted_data = fhe_engine.decrypt(encrypted_data)
    
    # 验证结果
    np.testing.assert_array_almost_equal(original_data, decrypted_data, decimal=4)

def test_homomorphic_addition(fhe_engine):
    """测试同态加法"""
    # 准备测试数据
    data = np.array([1.0, 2.0, 3.0])
    value_to_add = 5.0
    
    # 加密数据
    encrypted_data = fhe_engine.encrypt(data)
    
    # 执行同态加法
    encrypted_result = fhe_engine.compute(
        encrypted_data, 
        "add", 
        {"value": value_to_add}
    )
    
    # 解密结果
    result = fhe_engine.decrypt(encrypted_result)
    
    # 验证结果
    expected = data + value_to_add
    np.testing.assert_array_almost_equal(result, expected, decimal=4)

def test_homomorphic_mean(fhe_engine):
    """测试同态平均值计算"""
    # 准备测试数据
    data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    expected_mean = np.mean(data)
    
    # 加密数据
    encrypted_data = fhe_engine.encrypt(data)
    
    # 计算平均值
    encrypted_result = fhe_engine.compute(encrypted_data, "mean")
    
    # 解密结果
    result = fhe_engine.decrypt(encrypted_result)
    
    # 验证结果
    assert abs(result - expected_mean) < 1e-4

def test_invalid_operation(fhe_engine):
    """测试无效操作处理"""
    data = np.array([1.0, 2.0, 3.0])
    encrypted_data = fhe_engine.encrypt(data)
    
    with pytest.raises(ValueError):
        fhe_engine.compute(encrypted_data, "invalid_operation")