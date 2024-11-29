from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import logging
from ..core.node import CoordinatorNode
from ..core.data import DataManager

app = FastAPI()

class EONService:
    """EON协议API服务"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.coordinator = CoordinatorNode(config.get('coordinator', {}))
        self.data_manager = DataManager(config.get('data', {}))
        self.logger = logging.getLogger(__name__)
        
    @app.post("/compute")
    async def handle_computation(self, request: Dict[str, Any]):
        """处理计算请求"""
        try:
            # 加载数据
            data, metadata = self.data_manager.retrieve_data(request['data_id'])
            
            # 创建计算任务
            task = {
                'id': self._generate_task_id(),
                'data': data,
                'operation': request['operation'],
                'params': request.get('params')
            }
            
            # 执行计算
            result = self.coordinator.execute_task(task)
            
            # 存储结果
            result_id = self.data_manager.store_data(
                result,
                metadata={'task_id': task['id']}
            )
            
            return {'result_id': result_id}
            
        except Exception as e:
            self.logger.error(f"计算请求处理失败: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
            
    def _generate_task_id(self) -> str:
        """生成唯一任务ID"""
        import uuid
        return str(uuid.uuid4())