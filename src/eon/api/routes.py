
from fastapi import FastAPI, HTTPException, Depends
from typing import Dict, Any, Optional
import logging
from pydantic import BaseModel
from ..core.node import NodeManager
from ..core.scheduler import TaskManager
from ..utils.auth import AuthHandler

app = FastAPI(title="EON Protocol API")
logger = logging.getLogger(__name__)

class ComputeRequest(BaseModel):
    data_id: str
    operation: str
    params: Optional[Dict[str, Any]] = None

class ComputeResponse(BaseModel):
    task_id: str
    status: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: float
    result_id: Optional[str] = None
    error: Optional[str] = None

auth_handler = AuthHandler()
node_manager = NodeManager()
task_manager = TaskManager()

@app.post("/api/v1/compute", response_model=ComputeResponse)
async def compute(
    request: ComputeRequest,
    token: str = Depends(auth_handler.auth_wrapper)
):
    """提交计算任务"""
    try:
        # 创建任务
        task_id = task_manager.submit_task({
            'data_id': request.data_id,
            'operation': request.operation,
            'params': request.params
        })
        
        return ComputeResponse(
            task_id=task_id,
            status="submitted"
        )
    except Exception as e:
        logger.error(f"Failed to submit computation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    token: str = Depends(auth_handler.auth_wrapper)
):
    """获取任务状态"""
    try:
        status = task_manager.get_task_status(task_id)
        return TaskStatusResponse(**status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """健康检查接口"""
    try:
        node_status = node_manager.get_system_status()
        return {
            "status": "healthy",
            "nodes": node_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
