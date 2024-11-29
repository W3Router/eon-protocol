import grpc
from concurrent import futures
from typing import Dict, Any
import logging
from .proto import computation_pb2_grpc
from ..fhe.engine import FHEEngine

class ComputeNode:
    """计算节点，执行FHE计算"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.fhe_engine = FHEEngine(config.get('fhe', {}))
        self.node_id = config.get('node_id')
        self.status = 'IDLE'
        self.logger = logging.getLogger(__name__)
        self._setup_grpc_server()
        
    def _setup_grpc_server(self):
        """设置gRPC服务器"""
        self.server = grpc.server(
            futures.ThreadPoolExecutor(
                max_workers=self.config.get('max_workers', 5)
            )
        )
        computation_pb2_grpc.add_ComputationServicer_to_server(
            self, self.server
        )
        self.server.add_insecure_port(
            f"[::]:{self.config.get('port', 50052)}"
        )
        
    def start(self):
        """启动计算节点"""
        try:
            self.server.start()
            self._register_with_coordinator()
            self.logger.info(f"计算节点 {self.node_id} 已启动")
            self.server.wait_for_termination()
        except Exception as e:
            self.logger.error(f"计算节点启动失败: {str(e)}")
            raise
            
    def _register_with_coordinator(self):
        """向协调节点注册"""
        try:
            coordinator_address = self.config.get('coordinator_address')
            with grpc.insecure_channel(coordinator_address) as channel:
                stub = computation_pb2_grpc.CoordinatorStub(channel)
                registration_info = {
                    'id': self.node_id,
                    'address': f"localhost:{self.config.get('port')}",
                    'capabilities': self.config.get('capabilities', {})
                }
                stub.RegisterNode(registration_info)
        except Exception as e:
            self.logger.error(f"节点注册失败: {str(e)}")
            raise
            
    def execute_task(self, task: Dict[str, Any]):
        """执行计算任务"""
        try:
            self.status = 'BUSY'
            self.logger.info(f"开始执行任务: {task['id']}")
            
            # 执行FHE计算
            result = self.fhe_engine.compute(
                task['data'],
                task['operation'],
                task.get('params')
            )
            
            self.status = 'IDLE'
            self.logger.info(f"任务完成: {task['id']}")
            return result
            
        except Exception as e:
            self.status = 'ERROR'
            self.logger.error(f"任务执行失败: {str(e)}")
            raise
        finally:
            self.status = 'IDLE'