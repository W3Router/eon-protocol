import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

def test_compute_node_lifecycle(test_config):
    from eon.utils.config import Config
    from eon.core.node.compute import ComputeNode
    
    config = Config(test_config)
    node = ComputeNode(config)
    
    try:
        # 测试启动
        node.start()
        
        # 测试停止
        node.stop()
    except Exception as e:
        pytest.fail(f"Node lifecycle test failed: {str(e)}")

def test_computation_workflow(test_config):
    from eon.utils.config import Config
    from eon.core.node.compute import ComputeNode
    from eon.core.proto import computation_pb2
    
    config = Config(test_config)
    node = ComputeNode(config)
    
    # 测试提交计算
    submit_request = computation_pb2.ComputationRequest(
        data_id="test-data",
        operation="add",
        params=b'{"value": 1}'
    )
    submit_response = node.SubmitComputation(submit_request, None)
    assert submit_response.task_id is not None
    assert submit_response.status == "submitted"
    
    # 测试获取状态
    status_request = computation_pb2.TaskStatusRequest(
        task_id=submit_response.task_id
    )
    status_response = node.GetTaskStatus(status_request, None)
    assert status_response.task_id == submit_response.task_id
    assert status_response.status in ["running", "completed", "failed"]