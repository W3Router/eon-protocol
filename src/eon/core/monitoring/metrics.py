from typing import Dict, Any, List
import psutil
import time
import threading
import logging
from collections import deque

class MetricsCollector:
    """系统指标收集器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics_history = deque(maxlen=config.get('history_size', 1000))
        self.collection_interval = config.get('collection_interval', 5)
        self.running = False
        self.thread = None
        self.logger = logging.getLogger(__name__)

    def start(self):
        """启动指标收集"""
        self.running = True
        self.thread = threading.Thread(target=self._collect_loop)
        self.thread.daemon = True
        self.thread.start()
        self.logger.info("指标收集器已启动")

    def stop(self):
        """停止指标收集"""
        self.running = False
        if self.thread:
            self.thread.join()
        self.logger.info("指标收集器已停止")

    def _collect_loop(self):
        """指标收集循环"""
        while self.running:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                time.sleep(self.collection_interval)
            except Exception as e:
                self.logger.error(f"指标收集失败: {str(e)}")

    def _collect_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        return {
            "timestamp": time.time(),
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq()._asdict()
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "percent": psutil.disk_usage('/').percent
            },
            "network": psutil.net_io_counters()._asdict()
        }

    def get_metrics(self, 
                    start_time: Optional[float] = None, 
                    end_time: Optional[float] = None) -> List[Dict[str, Any]]:
        """获取指定时间范围的指标"""
        metrics = list(self.metrics_history)
        if start_time:
            metrics = [m for m in metrics if m["timestamp"] >= start_time]
        if end_time:
            metrics = [m for m in metrics if m["timestamp"] <= end_time]
        return metrics

class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.logger = logging.getLogger(__name__)

    def analyze_system_health(self) -> Dict[str, Any]:
        """分析系统健康状况"""
        try:
            metrics = self.metrics_collector.get_metrics()
            if not metrics:
                return {"status": "Unknown"}

            latest = metrics[-1]
            warnings = []

            # CPU使用率检查
            if latest["cpu"]["percent"] > 80:
                warnings.append("CPU使用率过高")

            # 内存使用率检查
            if latest["memory"]["percent"] > 85:
                warnings.append("内存使用率过高")

            # 磁盘使用率检查
            if latest["disk"]["percent"] > 90:
                warnings.append("磁盘使用率过高")

            status = "Healthy" if not warnings else "Warning"
            return {
                "status": status,
                "warnings": warnings,
                "metrics": latest
            }
        except Exception as e:
            self.logger.error(f"系统健康分析失败: {str(e)}")
            return {"status": "Error", "error": str(e)}