import grpc
from concurrent import futures
from typing import Dict, List, Any
import logging
from .proto import computation_pb2_grpc
from ..fhe.engine import FHEEngine

class CoordinatorNode:
    """协调节点，管理分布式计算"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.fhe_engine = FHEEngine(config.get('fhe', {}))
        self.compute_nodes = {}
        self.logger = logging.getLogger(__name__)
        self._setup_grpc_server()
        
    def _setup_grpc_server(self):
        """设置gRPC服务器"""
        self.server = grpc.server(
            futures.ThreadPoolExecutor(
                max_workers=self.config.get('max_workers', 10)
            )
        )
        computation_pb2_grpc.add_ComputationServicer_to_server(
            self, self.server
        )
        self.server.add_insecure_port(
            f"[::]:{self.config.get('port', 50051)}"
        )
        
    def start(self):
        """启动协调节点"""
        try:
            self.server.start()
            self.logger.info("协调节点已启动")
            self.server.wait_for_termination()
        except Exception as e:
            self.logger.error(f"协调节点启动失败: {str(e)}")
            raise
            
    def stop(self):
        """停止协调节点"""
        try:
            self.server.stop(0)
            self.logger.info("协调节点已停止")
        except Exception as e:
            self.logger.error(f"协调节点停止失败: {str(e)}")
            raise
            
    def register_node(self, node_info: Dict[str, Any]):
        """注册计算节点"""
        try:
            node_id = node_info['id']
            self.compute_nodes[node_id] = node_info
            self.logger.info(f"计算节点注册成功: {node_id}")
        except Exception as e:
            self.logger.error(f"计算节点注册失败: {str(e)}")
            raise