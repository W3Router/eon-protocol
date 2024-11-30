import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

def test_invalid_computation(test_config):
    from eon.utils.config import Config
    from eon.core.node.compute import ComputeNode
    from eon.core.proto import computation_pb2
    
    config = Config(test_config)
    node = ComputeNode(config)
    
    request = computation_pb2.ComputationRequest(
        data_id="test-data",
        operation="invalid_op"
    )
    response = node.SubmitComputation(request, None)
    assert response.status == "failed"
    assert response.task_id == "error"

def test_invalid_task_status(test_config):
    from eon.utils.config import Config
    from eon.core.node.compute import ComputeNode
    from eon.core.proto import computation_pb2
    
    config = Config(test_config)
    node = ComputeNode(config)
    
    request = computation_pb2.TaskStatusRequest(
        task_id="invalid-task-id"
    )
    response = node.GetTaskStatus(request, None)
    assert response.status == "error"