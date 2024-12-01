import pytest
import logging
from typing import Dict, Any

# 配置基础日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@pytest.fixture(scope="session")
def base_config() -> Dict[str, Any]:
    """提供基础配置"""
    return {
        'coordinator': {
            'host': 'localhost',
            'port': 50051,
            'max_workers': 40  # 增加worker数量以支持更多节点
        },
        'compute_node': {
            'host': 'localhost',
            'base_port': 50052,
            'max_workers': 5
        }
    }

@pytest.fixture(scope="session")
def performance_config() -> Dict[str, Any]:
    """性能测试配置"""
    return {
        'node_counts': [2, 4, 20],  # 测试2、4和20个节点
        'data_sizes': [1000, 5000, 10000],  # 增加数据规模
        'batch_sizes': [100, 500, 1000],  # 增加批处理大小选项
        'test_duration': 60,  # 测试持续时间（秒）
        'warmup_duration': 10,  # 预热时间（秒）
        'metrics_interval': 1.0  # 指标收集间隔（秒）
    }


@pytest.fixture
def logger():
    """Fixture to provide a configured logger for tests"""
    # Create logger
    logger = logging.getLogger('performance_test')
    logger.setLevel(logging.INFO)
    
    # Create console handler and set level to INFO
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add formatter to ch
    ch.setFormatter(formatter)
    
    # Add ch to logger
    logger.addHandler(ch)
    
    return logger

# You might also want to add a more specialized performance logger
@pytest.fixture
def performance_logger(logger):
    """Fixture to provide a logger specifically for performance metrics"""
    perf_logger = logger.getChild('performance')
    return perf_logger
