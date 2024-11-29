import pytest
import numpy as np
from eon.core.node import CoordinatorNode, ComputeNode
from eon.utils.config import Config
import time

@pytest.fixture
def system_setup():
    """设置测试环境"""
    # 加载测试配置
    config = {
        "coordinator": {
            "port": 50051,
            "max_workers": 2
        },
        "compute_node": {
            "port": 50052,
            "max_workers": 1
        },
        "fhe": {
            "poly_modulus_degree": 8192,
            "coeff_mod_bit_sizes": [60, 40, 40, 60]
        }
    }
    
    # 创建协调节点
    coordinator = CoordinatorNode(config["coordinator"])
    coordinator.start_async()
    
    # 创建计算节点
    compute_node = ComputeNode(config["compute_node"])
    compute_node.start_async()
    
    # 等待系统初始化
    time.sleep(2)
    
    yield coordinator, compute_node
    
    # 清理
    compute_node.stop()
    coordinator.stop()

def test_distributed_computation(system_setup):
    """测试分布式计算流程"""
    coordinator, _ = system_setup
    
    # 准备测试数据
    data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    expected_mean = np.mean(data)
    
    # 创建计算任务
    task = {
        "id": "test-task-1",
        "data": data,
        "operation": "mean"
    }
    
    # 执行任务
    result = coordinator.execute_task(task)
    
    # 验证结果
    assert abs(result - expected_mean) < 1e-4

def test_multi_node_computation(system_setup):
    """测试多节点计算"""
    coordinator, _ = system_setup
    
    # 准备大量数据
    data = np.random.rand(1000)
    expected_mean = np.mean(data)
    
    # 创建多个任务
    tasks = [
        {
            "id": f"test-task-{i}",
            "data": data[i*200:(i+1)*200],
            "operation": "mean"
        }
        for i in range(5)
    ]
    
    # 执行任务并收集结果
    results = []
    for task in tasks:
        result = coordinator.execute_task(task)
        results.append(result)
    
    # 计算最终结果
    final_result = np.mean(results)
    
    # 验证结果
    assert abs(final_result - expected_mean) < 1e-4