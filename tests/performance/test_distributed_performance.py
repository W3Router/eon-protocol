# tests/performance/test_distributed_performance.py
import pytest
import sys
import os
import time
import yaml
import json
import numpy as np
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_single_node_performance():
    """测试单节点性能"""
    from eon.utils.config import Config
    from eon.core.node.compute import ComputeNode
    from eon.core.proto import computation_pb2

    # 设置节点
    config_data = {
        "node": {
            "type": "compute",
            "id": "single-node",
            "host": "localhost",
            "port": 50051
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
    
    config_path = "test_config_single.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    
    config = Config(config_path)
    node = ComputeNode(config)
    node.start()

    try:
        # 执行测试任务
        total_tasks = 100
        completed = 0
        errors = 0
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(total_tasks):
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
        
        print("\nSingle Node Performance Results:")
        print(f"Total tasks: {total_tasks}")
        print(f"Completed: {completed}")
        print(f"Errors: {errors}")
        print(f"Duration: {duration:.2f}s")
        print(f"Throughput: {completed/duration:.2f} tasks/s")

        assert completed > 0, "No tasks completed successfully"
        assert errors == 0, f"Had {errors} errors during execution"

    finally:
        node.stop()
        os.remove(config_path)

def test_distributed_performance():
    """测试分布式性能"""
    from eon.utils.config import Config
    from eon.core.node.compute import ComputeNode
    from eon.core.proto import computation_pb2

    nodes = []
    config_files = []
    node_count = 3
    base_port = 50051

    # 创建多个节点
    for i in range(node_count):
        config_data = {
            "node": {
                "type": "compute",
                "id": f"node-{i}",
                "host": "localhost",
                "port": base_port + i
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
        
        config_path = f"test_config_node_{i}.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        
        config_files.append(config_path)
        config = Config(config_path)
        node = ComputeNode(config)
        node.start()
        nodes.append(node)

    try:
        # 执行测试任务
        total_tasks = 100
        completed = 0
        errors = 0
        start_time = time.time()

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
        
        print("\nDistributed Performance Results:")
        print(f"Nodes: {node_count}")
        print(f"Total tasks: {total_tasks}")
        print(f"Completed: {completed}")
        print(f"Errors: {errors}")
        print(f"Duration: {duration:.2f}s")
        print(f"Throughput: {completed/duration:.2f} tasks/s")

        assert completed > 0, "No tasks completed successfully"
        assert errors == 0, f"Had {errors} errors during execution"

    finally:
        for node in nodes:
            node.stop()
        for config_file in config_files:
            os.remove(config_file)
