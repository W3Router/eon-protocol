```python
import grpc
from typing import Dict, Any, Optional
import logging
from ..proto import computation_pb2, computation_pb2_grpc

class ComputationClient:
    """节点间通信客户端"""
    
    def __init__(self, target: str):
        self.target = target
        self.channel = grpc.insecure_channel(target)
        self.stub = computation_pb2_grpc.ComputationServiceStub(self.channel)
        self.logger = logging.getLogger(__name__)

    def register_node(self, 
                     node_id: str, 
                     address: str,
                     capabilities: Dict[str, str]) -> bool:
        """注册节点到协调器"""
        try:
            request = computation_pb2.RegisterNodeRequest(
                node_id=node_id,
                address=address,
                capabilities=capabilities
            )
            response = self.stub.RegisterNode(request)
            return response.success
        except Exception as e:
            self.logger.error(f"节点注册请求失败: {str(e)}")
            return False

    def execute_computation(self,
                          task_id: str,
                          encrypted_data: bytes,
                          operation: str,
                          parameters: Dict[str, bytes]) -> Optional[bytes]:
        """发送计算请求"""
        try:
            request = computation_pb2.ComputationRequest(
                task_id=task_id,
                encrypted_data=encrypted_data,
                operation=operation,
                parameters=parameters
            )
            response = self.stub.ExecuteComputation(request)
            if response.success:
                return response.result
            else:
                self.logger.error(f"计算执行失败: {response.error_message}")
                return None
        except Exception as e:
            self.logger.error(f"发送计算请求失败: {str(e)}")
            return None

    def get_node_status(self, node_id: str) -> Dict[str, Any]:
        """获取节点状态"""
        try:
            request = computation_pb2.NodeStatusRequest(node_id=node_id)
            response = self.stub.GetNodeStatus(request)
            return {
                'node_id': response.node_id,
                'status': response.status,
                'active_tasks': response.active_tasks,
                'metrics': dict(response.metrics)
            }
        except Exception as e:
            self.logger.error(f"获取节点状态失败: {str(e)}")
            return {}

    def close(self):
        """关闭通信通道"""
        try:
            self.channel.close()
        except Exception as e:
            self.logger.error(f"关闭通信通道失败: {str(e)}")
```