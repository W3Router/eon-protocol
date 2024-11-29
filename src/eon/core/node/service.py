```python
import grpc
from concurrent import futures
from typing import Dict, Any
import logging
from ..proto import computation_pb2, computation_pb2_grpc
from ..fhe.engine import FHEEngine

class ComputationServicer(computation_pb2_grpc.ComputationServiceServicer):
    """gRPC服务实现"""
    
    def __init__(self, node_manager):
        self.node_manager = node_manager
        self.fhe_engine = FHEEngine()
        self.logger = logging.getLogger(__name__)

    async def RegisterNode(self, request, context):
        """处理节点注册请求"""
        try:
            node_info = {
                'id': request.node_id,
                'address': request.address,
                'capabilities': dict(request.capabilities)
            }
            self.node_manager.register_node(node_info)
            return computation_pb2.RegisterNodeResponse(
                success=True,
                message="Registration successful"
            )
        except Exception as e:
            self.logger.error(f"Node registration failed: {str(e)}")
            return computation_pb2.RegisterNodeResponse(
                success=False,
                message=str(e)
            )

    async def ExecuteComputation(self, request, context):
        """处理计算请求"""
        try:
            # 解析加密数据
            encrypted_data = self.fhe_engine.deserialize(request.encrypted_data)
            
            # 执行计算
            result = self.fhe_engine.compute(
                encrypted_data,
                request.operation,
                dict(request.params)
            )
            
            # 序列化结果
            serialized_result = self.fhe_engine.serialize(result)
            
            return computation_pb2.ComputationResponse(
                task_id=request.task_id,
                result=serialized_result,
                success=True
            )
        except Exception as e:
            self.logger.error(f"Computation failed: {str(e)}")
            return computation_pb2.ComputationResponse(
                task_id=request.task_id,
                success=False,
                error_message=str(e)
            )
```