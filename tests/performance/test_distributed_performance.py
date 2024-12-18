# tests/performance/test_distributed_performance.py
import pytest
import sys
import os
import time
import yaml
import json
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from eon.utils.config import Config
from eon.core.node.compute import ComputeNode
from eon.core.proto import computation_pb2

def create_node_config(node_id: str, port: int) -> Dict[str, Any]:
    """创建节点配置"""
    return {
        "node": {
            "type": "compute",
            "id": node_id,
            "host": "localhost",
            "port": port
        },
        "fhe": {
            "scheme": "CKKS",
            "poly_modulus_degree": 8192,
            "coeff_mod_bit_sizes": [60, 40, 40, 60]
        },
        "grpc": {
            "max_workers": multiprocessing.cpu_count()
        }
    }

def setup_node(config_data: Dict[str, Any], config_path: str) -> ComputeNode:
    """设置并启动节点"""
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    
    config = Config(config_path)
    node = ComputeNode(config)
    node.start()
    return node

def run_performance_test(nodes: List[ComputeNode], total_tasks: int) -> tuple:
    """执行性能测试"""
    completed = 0
    errors = 0
    start_time = time.time()
    node_count = len(nodes)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for i in range(total_tasks):
            node = nodes[i % node_count]
            request = computation_pb2.ComputationRequest(
                data_id=f"test-data-{i}",
                operation="add",
                params=json.dumps({"value": 1.0}).encode()
            )
            futures.append(executor.submit(node.SubmitComputation, request, None))

        for future in as_completed(futures):
            try:
                response = future.result()
                if response.status == "submitted":
                    completed += 1
                else:
                    errors += 1
            except Exception as e:
                print(f"Error: {e}")
                errors += 1

    duration = time.time() - start_time
    return completed, errors, duration

def print_performance_results(test_type: str, node_count: int, total_tasks: int,
                            completed: int, errors: int, duration: float) -> None:
    """打印性能测试结果"""
    print(f"\n{test_type} Performance Results:")
    if node_count > 1:
        print(f"Nodes: {node_count}")
    print(f"Total tasks: {total_tasks}")
    print(f"Completed: {completed}")
    print(f"Errors: {errors}")
    print(f"Duration: {duration:.2f}s")
    print(f"Throughput: {completed/duration:.2f} tasks/s")

def analyze_performance_metrics(node_count: int, total_tasks: int, completed: int, 
                              duration: float, errors: int) -> Dict[str, float]:
    """分析性能指标
    
    Args:
        node_count: 节点数量
        total_tasks: 总任务数
        completed: 完成的任务数
        duration: 执行时间
        errors: 错误数
    
    Returns:
        包含各项性能指标的字典
    """
    metrics = {
        'throughput': completed / duration,  # 总吞吐量
        'per_node_throughput': (completed / duration) / node_count,  # 每节点吞吐量
        'completion_rate': completed / total_tasks * 100,  # 完成率
        'error_rate': errors / total_tasks * 100,  # 错误率
        'avg_task_duration': duration / completed if completed > 0 else 0,  # 平均任务处理时间
        'efficiency': (completed / duration) / node_count / 10  # 效率指标（归一化到0-1）
    }
    return metrics

def print_analysis_results(metrics: Dict[str, float], node_count: int):
    """打印分析结果"""
    print("\nPerformance Analysis:")
    print(f"Overall Throughput: {metrics['throughput']:.2f} tasks/s")
    print(f"Per-node Throughput: {metrics['per_node_throughput']:.2f} tasks/s/node")
    print(f"Completion Rate: {metrics['completion_rate']:.2f}%")
    print(f"Error Rate: {metrics['error_rate']:.2f}%")
    print(f"Average Task Duration: {metrics['avg_task_duration']*1000:.2f} ms")
    print(f"System Efficiency: {metrics['efficiency']*100:.2f}%")
    
    # 性能评级
    if metrics['efficiency'] >= 0.8:
        rating = "Excellent"
    elif metrics['efficiency'] >= 0.6:
        rating = "Good"
    elif metrics['efficiency'] >= 0.4:
        rating = "Fair"
    else:
        rating = "Poor"
    
    print(f"\nPerformance Rating: {rating}")
    
    # 扩展性分析
    if node_count > 1:
        scalability = metrics['per_node_throughput'] * node_count / 100
        print(f"Scalability Factor: {scalability:.2f}")
        if scalability >= 0.9:
            print("Near-linear scaling")
        elif scalability >= 0.7:
            print("Sub-linear scaling")
        else:
            print("Poor scaling - bottleneck detected")

def test_single_node_performance():
    """测试单节点性能"""
    config_path = "test_config_single.yaml"
    config_data = create_node_config("single-node", 50051)
    node = setup_node(config_data, config_path)

    try:
        completed, errors, duration = run_performance_test([node], 100)
        print_performance_results("Single Node", 1, 100, completed, errors, duration)

        assert completed > 0, "No tasks completed successfully"
        assert errors == 0, f"Had {errors} errors during execution"

    finally:
        node.stop()
        os.remove(config_path)

@pytest.mark.parametrize("node_count,total_tasks", [
    (4, 200),    # 4节点测试
    (20, 1000),  # 20节点测试
    pytest.param(100, 5000, marks=pytest.mark.large)  # 100节点测试，标记为大规模测试
])
def test_multi_scale_performance(node_count: int, total_tasks: int):
    """测试不同规模节点的分布式性能
    
    Args:
        node_count: 节点数量
        total_tasks: 总任务数
    """
    nodes = []
    config_files = []
    base_port = 50051

    print(f"\nSetting up {node_count} nodes for performance testing...")
    
    # 创建多个节点
    for i in range(node_count):
        config_path = f"test_config_node_{i}.yaml"
        config_data = create_node_config(f"node-{i}", base_port + i)
        try:
            nodes.append(setup_node(config_data, config_path))
            config_files.append(config_path)
        except Exception as e:
            print(f"Failed to setup node {i}: {e}")
            # 清理已创建的节点
            for node in nodes:
                node.stop()
            for config_file in config_files:
                if os.path.exists(config_file):
                    os.remove(config_file)
            raise

    try:
        print(f"Starting performance test with {total_tasks} tasks...")
        completed, errors, duration = run_performance_test(nodes, total_tasks)
        print_performance_results(
            f"Large Scale ({node_count} nodes)", 
            node_count, 
            total_tasks, 
            completed, 
            errors, 
            duration
        )
        
        # 添加性能分析
        metrics = analyze_performance_metrics(
            node_count, total_tasks, completed, duration, errors
        )
        print_analysis_results(metrics, node_count)
        
        # 将结果保存到文件（可选）
        results_file = f"performance_results_{node_count}nodes.json"
        with open(results_file, "w") as f:
            json.dump({
                "node_count": node_count,
                "total_tasks": total_tasks,
                "metrics": metrics
            }, f, indent=2)
            
        # 计算每个节点的平均处理任务数
        avg_tasks_per_node = completed / node_count
        print(f"Average tasks per node: {avg_tasks_per_node:.2f}")
        
        # 添加更详细的断言
        assert completed > 0, "No tasks completed successfully"
        assert errors == 0, f"Had {errors} errors during execution"
        assert completed >= total_tasks * 0.95, f"Completion rate too low: {completed/total_tasks:.2%}"
        assert duration > 0, "Invalid duration measurement"

    finally:
        print("Cleaning up test environment...")
        for node in nodes:
            try:
                node.stop()
            except Exception as e:
                print(f"Error stopping node: {e}")
        
        for config_file in config_files:
            try:
                if os.path.exists(config_file):
                    os.remove(config_file)
            except Exception as e:
                print(f"Error removing config file {config_file}: {e}")
