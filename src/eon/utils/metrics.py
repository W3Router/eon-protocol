```python
from typing import Dict, Any, List
import time
from collections import defaultdict
import threading
import psutil
import logging

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

    def record_request_metrics(self, data: Dict[str, Any]):
        """记录请求指标"""
        with self.lock:
            self.metrics['requests'].append({
                'timestamp': time.time(),
                **data
            })

    def record_computation_metrics(self, data: Dict[str, Any]):
        """记录计算指标"""
        with self.lock:
            self.metrics['computations'].append({
                'timestamp': time.time(),
                **data
            })

    def record_system_metrics(self):
        """记录系统指标"""
        with self.lock:
            self.metrics['system'].append({
                'timestamp': time.time(),
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent
            })

    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        with self.lock:
            return {
                'requests': self._summarize_requests(),
                'computations': self._summarize_computations(),
                'system': self._summarize_system()
            }

    def _summarize_requests(self) -> Dict[str, Any]:
        """汇总请求指标"""
        requests = self.metrics['requests']
        if not requests:
            return {}
            
        return {
            'total_count': len(requests),
            'average_duration': sum(r['duration'] for r in requests) / len(requests),
            'status_codes': self._count_status_codes(requests),
            'paths': self._count_paths(requests)
        }

    def _summarize_computations(self) -> Dict[str, Any]:
        """汇总计算指标"""
        computations = self.metrics['computations']
        if not computations:
            return {}
            
        return {
            'total_count': len(computations),
            'average_duration': sum(c['duration'] for c in computations) / len(computations),
            'success_rate': sum(1 for c in computations if c['success']) / len(computations)
        }

    def _summarize_system(self) -> Dict[str, Any]:
        """汇总系统指标"""
        system = self.metrics['system']
        if not system:
            return {}
            
        return {
            'average_cpu': sum(s['cpu_percent'] for s in system) / len(system),
            'average_memory': sum(s['memory_percent'] for s in system) / len(system),
            'average_disk': sum(s['disk_usage'] for s in system) / len(system)
        }

    def _count_status_codes(self, requests: List[Dict[str, Any]]) -> Dict[int, int]:
        """统计状态码"""
        counter = defaultdict(int)
        for request in requests:
            counter[request['status_code']] += 1
        return dict(counter)

    def _count_paths(self, requests: List[Dict[str, Any]]) -> Dict[str, int]:
        """统计路径访问"""
        counter = defaultdict(int)
        for request in requests:
            counter[request['path']] += 1
        return dict(counter)

    def clear_metrics(self):
        """清除指标数据"""
        with self.lock:
            self.metrics.clear()
```
