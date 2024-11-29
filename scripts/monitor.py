```python
import psutil
import time
import logging
import requests
from typing import Dict, Any
import yaml

class SystemMonitor:
    """系统监控器"""

    def __init__(self, config_path: str):
        self.load_config(config_path)
        self.setup_logging()

    def load_config(self, config_path: str):
        """加载配置"""
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='/var/log/eon/monitor.log'
        )
        self.logger = logging.getLogger(__name__)

    def collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network': psutil.net_io_counters()._asdict()
        }

    def check_service_health(self) -> Dict[str, bool]:
        """检查服务健康状态"""
        services = {
            'coordinator': f"http://{self.config['coordinator']['host']}:{self.config['coordinator']['port']}/health",
            'api': f"http://{self.config['api']['host']}:{self.config['api']['port']}/health"
        }

        health_status = {}
        for name, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                health_status[name] = response.status_code == 200
            except Exception as e:
                self.logger.error(f"服务 {name} 健康检查失败: {str(e)}")
                health_status[name] = False

        return health_status

    def monitor(self):
        """运行监控循环"""
        while True:
            try:
                # 收集指标
                metrics = self.collect_system_metrics()
                self.logger.info(f"系统指标: {metrics}")

                # 检查服务健康状态
                health = self.check_service_health()
                self.logger.info(f"服务健康状态: {health}")

                # 检查警告条件
                if metrics['cpu_percent'] > 80:
                    self.logger.warning("CPU使用率过高")
                if metrics['memory_percent'] > 85:
                    self.logger.warning("内存使用率过高")
                if metrics['disk_usage'] > 90:
                    self.logger.warning("磁盘使用率过高")

                # 检查服务状态
                for service, is_healthy in health.items():
                    if not is_healthy:
                        self.logger.error(f"服务 {service} 不健康")

                time.sleep(60)  # 每分钟检查一次

            except Exception as e:
                self.logger.error(f"监控过程出错: {str(e)}")
                time.sleep(60)  # 发生错误时等待一分钟再重试

def main():
    import argparse
    parser = argparse.ArgumentParser(description='EON系统监控工具')
    parser.add_argument('--config', required=True, help='配置文件路径')
    args = parser.parse_args()

    monitor = SystemMonitor(args.config)
    monitor.monitor()

if __name__ == '__main__':
    main()
```