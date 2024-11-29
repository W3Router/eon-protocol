```python
from typing import Dict, Any
import psutil
import logging
from datetime import datetime
import aiohttp
import asyncio

class HealthChecker:
    """系统健康检查器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    async def check_system_health(self) -> Dict[str, Any]:
        """检查系统健康状态"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status = "healthy"
            warnings = []
            
            # 检查CPU使用率
            if cpu_percent > 80:
                warnings.append("High CPU usage")
                status = "warning"
                
            # 检查内存使用率
            if memory.percent > 85:
                warnings.append("High memory usage")
                status = "warning"
                
            # 检查磁盘使用率
            if disk.percent > 90:
                warnings.append("High disk usage")
                status = "warning"
                
            return {
                'status': status,
                'timestamp': datetime.now().isoformat(),
                'metrics': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent
                },
                'warnings': warnings
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
            
    async def check_service_health(self) -> Dict[str, Any]:
        """检查服务健康状态"""
        services = {
            'coordinator': f"http://{self.config['coordinator']['host']}:{self.config['coordinator']['port']}/health",
            'api': f"http://{self.config['api']['host']}:{self.config['api']['port']}/health"
        }
        
        results = {}
        async with aiohttp.ClientSession() as session:
            for name, url in services.items():
                try:
                    async with session.get(url) as response:
                        results[name] = {
                            'status': 'healthy' if response.status == 200 else 'unhealthy',
                            'response_time': response.elapsed.total_seconds()
                        }
                except Exception as e:
                    results[name] = {
                        'status': 'error',
                        'error': str(e)
                    }
                    
        return results
        
    async def run_health_check(self) -> Dict[str, Any]:
        """运行完整健康检查"""
        system_health = await self.check_system_health()
        service_health = await self.check_service_health()
        
        overall_status = 'healthy'
        if system_health['status'] != 'healthy' or \
           any(s['status'] != 'healthy' for s in service_health.values()):
            overall_status = 'warning'
            
        if system_health['status'] == 'error' or \
           any(s['status'] == 'error' for s in service_health.values()):
            overall_status = 'error'
            
        return {
            'status': overall_status,
            'timestamp': datetime.now().isoformat(),
            'system': system_health,
            'services': service_health
        }
```
