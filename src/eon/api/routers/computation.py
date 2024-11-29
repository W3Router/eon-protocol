```python
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from ..schemas.computation import (
    ComputationRequest,
    ComputationResponse,
    TaskStatusResponse
)
from ..dependencies import get_task_manager, get_auth_handler
from ...core.scheduler import TaskManager
from ...utils.logger import get_logger

router = APIRouter(prefix="/api/v1/computation", tags=["computation"])
logger = get_logger(__name__)

@router.post("/", response_model=ComputationResponse)
async def submit_computation(
    request: ComputationRequest,
    task_manager: TaskManager = Depends(get_task_manager),
    auth_handler = Depends(get_auth_handler)
):
    """提交计算任务"""
    try:
        task_id = await task_manager.submit_task(
            task_type="computation",
            data={
                "operation": request.operation,
                "data_id": request.data_id,
                "params": request.params
            }
        )
        
        return ComputationResponse(
            task_id=task_id,
            status="submitted"
        )
    except Exception as e:
        logger.error(f"Failed to submit computation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    task_manager: TaskManager = Depends(get_task_manager),
    auth_handler = Depends(get_auth_handler)
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
```