
from typing import Dict, Any, Optional, List, Callable
import asyncio
from datetime import datetime
import uuid
from dataclasses import dataclass
import logging
from ..utils.logger import get_logger

@dataclass
class Task:
    """任务数据类"""
    id: str
    type: str
    data: Dict[str, Any]
    priority: int
    created_at: datetime
    status: str = 'pending'
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class TaskQueue:
    """任务队列管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tasks: Dict[str, Task] = {}
        self.queue = asyncio.PriorityQueue()
        self.handlers: Dict[str, Callable] = {}
        self.logger = get_logger(__name__)
        self.running = False
        self.workers = []

    async def submit_task(self, task_type: str, 
                         data: Dict[str, Any], 
                         priority: int = 1) -> str:
        """提交新任务"""
        try:
            task_id = str(uuid.uuid4())
            task = Task(
                id=task_id,
                type=task_type,
                data=data,
                priority=priority,
                created_at=datetime.now()
            )
            
            self.tasks[task_id] = task
            await self.queue.put((priority, task_id))
            
            self.logger.info(f"Task submitted: {task_id}", 
                           extra={'task_type': task_type})
            return task_id
            
        except Exception as e:
            self.logger.error(f"Failed to submit task: {str(e)}")
            raise

    async def process_tasks(self):
        """处理任务队列"""
        self.running = True
        
        while self.running:
            try:
                # 获取任务
                _, task_id = await self.queue.get()
                task = self.tasks[task_id]
                
                # 更新任务状态
                task.status = 'running'
                task.started_at = datetime.now()
                
                # 执行任务
                if task.type in self.handlers:
                    try:
                        handler = self.handlers[task.type]
                        result = await handler(task.data)
                        
                        task.result = result
                        task.status = 'completed'
                        
                    except Exception as e:
                        task.error = str(e)
                        task.status = 'failed'
                        self.logger.error(f"Task failed: {task_id}", 
                                        exc_info=True)
                else:
                    task.error = f"No handler for task type: {task.type}"
                    task.status = 'failed'
                
                task.completed_at = datetime.now()
                self.queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Task processing error: {str(e)}")
                await asyncio.sleep(1)

    def register_handler(self, task_type: str, 
                        handler: Callable[[Dict[str, Any]], Any]):
        """注册任务处理器"""
        self.handlers[task_type] = handler

    async def start_workers(self, num_workers: int = 3):
        """启动工作进程"""
        self.workers = [
            asyncio.create_task(self.process_tasks())
            for _ in range(num_workers)
        ]

    async def stop(self):
        """停止任务队列"""
        self.running = False
        if self.workers:
            await asyncio.gather(*self.workers)
        
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        if task_id not in self.tasks:
            raise ValueError(f"Task not found: {task_id}")
            
        task = self.tasks[task_id]
        return {
            'id': task.id,
            'type': task.type,
            'status': task.status,
            'created_at': task.created_at.isoformat(),
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'result': task.result,
            'error': task.error
        }

    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """获取待处理任务"""
        return [
            self.get_task_status(task.id)
            for task in self.tasks.values()
            if task.status == 'pending'
        ]

    def clean_completed_tasks(self, max_age_hours: int = 24):
        """清理已完成的任务"""
        current_time = datetime.now()
        for task_id, task in list(self.tasks.items()):
            if task.status in ['completed', 'failed']:
                age = (current_time - task.completed_at).total_seconds() / 3600
                if age > max_age_hours:
                    del self.tasks[task_id]
