from typing import Dict, List, Any, Optional
from queue import PriorityQueue
import threading
import logging
import time

class Task:
    def __init__(self, task_id: str, priority: int, data: Any, operation: str, params: Optional[Dict] = None):
        self.id = task_id
        self.priority = priority
        self.data = data
        self.operation = operation
        self.params = params or {}
        self.status = "PENDING"
        self.created_at = time.time()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None

class TaskManager:
    """任务管理器，处理任务调度和执行"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.task_queue = PriorityQueue()
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        self.max_concurrent_tasks = config.get('max_concurrent_tasks', 10)

    def submit_task(self, task: Task) -> str:
        """提交新任务"""
        try:
            with self.lock:
                self.task_queue.put((task.priority, task))
                self.logger.info(f"任务提交成功: {task.id}")
            return task.id
        except Exception as e:
            self.logger.error(f"任务提交失败: {str(e)}")
            raise

    def get_next_task(self) -> Optional[Task]:
        """获取下一个待执行任务"""
        try:
            if self.task_queue.empty():
                return None
            if len(self.active_tasks) >= self.max_concurrent_tasks:
                return None
            
            _, task = self.task_queue.get_nowait()
            with self.lock:
                task.status = "ACTIVE"
                task.started_at = time.time()
                self.active_tasks[task.id] = task
            return task
        except Exception as e:
            self.logger.error(f"获取任务失败: {str(e)}")
            return None

    def complete_task(self, task_id: str, result: Any = None, error: Any = None):
        """完成任务处理"""
        try:
            with self.lock:
                if task_id in self.active_tasks:
                    task = self.active_tasks.pop(task_id)
                    task.completed_at = time.time()
                    task.result = result
                    task.error = error
                    task.status = "COMPLETED" if error is None else "FAILED"
                    self.completed_tasks[task_id] = task
                    self.logger.info(f"任务完成: {task_id}")
        except Exception as e:
            self.logger.error(f"任务完成处理失败: {str(e)}")
            raise

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        task = (self.active_tasks.get(task_id) or 
                self.completed_tasks.get(task_id))
        if task is None:
            raise ValueError(f"任务不存在: {task_id}")
            
        return {
            "id": task.id,
            "status": task.status,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "error": task.error
        }