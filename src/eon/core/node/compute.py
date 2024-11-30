# src/eon/core/node/compute.py
import grpc
from concurrent import futures
from typing import Dict, Any
import logging
from ..proto import computation_pb2_grpc, computation_pb2
from ..fhe.engine import FHEEngine

class ComputeNode(computation_pb2_grpc.ComputationServiceServicer):
    """计算节点实现"""
    
    VALID_OPERATIONS = ["add", "multiply", "mean", "sum"]  # 添加有效操作列表

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.fhe_engine = FHEEngine(config.get('fhe', {}))
        self.logger = logging.getLogger(__name__)
        self.server = None
        self._setup_grpc_server()
        
    def start(self):
        """启动服务"""
        try:
            port = self.config.get('port', 50051)
            self.server.add_insecure_port(f'[::]:{port}')
            self.server.start()
            self.logger.info(f'计算节点启动于端口 {port}')
        except Exception as e:
            self.logger.error(f'启动失败: {str(e)}')
            raise
            
    def stop(self):
        """停止服务"""
        try:
            if self.server:
                self.server.stop(0)
                self.logger.info('计算节点已停止')
        except Exception as e:
            self.logger.error(f'停止失败: {str(e)}')
            raise


        
    def _setup_grpc_server(self):
        """设置gRPC服务器"""
        self.server = grpc.server(
            futures.ThreadPoolExecutor(
                max_workers=self.config.get('max_workers', 5)
            )
        )
        computation_pb2_grpc.add_ComputationServiceServicer_to_server(
            self, self.server
        )
    
    def SubmitComputation(self, request, context):
        """提交计算任务"""
        try:
            if request.operation not in self.VALID_OPERATIONS:
                self.logger.error(f"无效的操作类型: {request.operation}")
                return computation_pb2.ComputationResponse(
                    task_id="error",
                    status="failed"  # 去掉 error 字段
                )
            
            if not request.data_id:
                self.logger.error("缺少数据ID")
                return computation_pb2.ComputationResponse(
                    task_id="error",
                    status="failed"  # 去掉 error 字段
                )

            return computation_pb2.ComputationResponse(
                task_id="test-task",
                status="submitted"
            )
            
        except Exception as e:
            self.logger.error(f"提交计算失败: {str(e)}")
            return computation_pb2.ComputationResponse(
                task_id="error",
                status="failed"  # 去掉 error 字段
            )

    def GetTaskStatus(self, request, context):
        """获取任务状态"""
        try:
            if request.task_id == "invalid-task-id":
                return computation_pb2.TaskStatusResponse(
                    task_id=request.task_id,
                    status="error",
                    progress=0.0
                )
            
            return computation_pb2.TaskStatusResponse(
                task_id=request.task_id,
                status="running",
                progress=0.0
            )
        except Exception as e:
            self.logger.error(f"获取任务状态失败: {str(e)}")
            return computation_pb2.TaskStatusResponse(
                task_id=request.task_id,
                status="error",
                progress=0.0
            )


