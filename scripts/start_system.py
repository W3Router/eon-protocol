```python
#!/usr/bin/env python
import os
import sys
import time
import logging
import subprocess
from typing import List, Dict
import yaml
import argparse

class SystemManager:
    """系统管理器"""
    
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.processes: Dict[str, subprocess.Popen] = {}
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='system.log'
        )
        return logging.getLogger(__name__)

    def start_coordinator(self):
        """启动协调节点"""
        try:
            cmd = [
                sys.executable,
                "-m",
                "eon",
                "--config",
                self.config_path,
                "--mode",
                "coordinator"
            ]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['coordinator'] = process
            self.logger.info("协调节点启动成功")
        except Exception as e:
            self.logger.error(f"协调节点启动失败: {str(e)}")
            raise

    def start_compute_nodes(self, num_nodes: int):
        """启动计算节点"""
        try:
            for i in range(num_nodes):
                cmd = [
                    sys.executable,
                    "-m",
                    "eon",
                    "--config",
                    self.config_path,
                    "--mode",
                    "compute",
                    "--node-id",
                    f"node-{i}"
                ]
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.processes[f'compute-{i}'] = process
            self.logger.info(f"启动了 {num_nodes} 个计算节点")
        except Exception as e:
            self.logger.error(f"计算节点启动失败: {str(e)}")
            raise

    def start_api_server(self):
        """启动API服务器"""
        try:
            cmd = [
                sys.executable,
                "-m",
                "eon",
                "--config",
                self.config_path,
                "--mode",
                "api"
            ]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['api'] = process
            self.logger.info("API服务器启动成功")
        except Exception as e:
            self.logger.error(f"API服务器启动失败: {str(e)}")
            raise

    def monitor_processes(self):
        """监控进程状态"""
        while True:
            for name, process in self.processes.items():
                if process.poll() is not None:
                    self.logger.error(f"进程 {name} 异常退出")
                    # 重启进程
                    self.restart_process(name)
            time.sleep(5)

    def restart_process(self, name: str):
        """重启进程"""
        try:
            if name.startswith('compute-'):
                node_id = name.split('-')[1]
                self.start_compute_nodes(1)
            elif name == 'coordinator':
                self.start_coordinator()
            elif name == 'api':
                self.start_api_server()
            self.logger.info(f"进程 {name} 重启成功")
        except Exception as e:
            self.logger.error(f"进程 {name} 重启失败: {str(e)}")

    def stop_all(self):
        """停止所有进程"""
        for name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                self.logger.info(f"进程 {name} 已停止")
            except subprocess.TimeoutExpired:
                process.kill()
                self.logger.warning(f"进程 {name} 被强制终止")
            except Exception as e:
                self.logger.error(f"停止进程 {name} 时出错: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='EON系统管理器')
    parser.add_argument('--config', required=True, help='配置文件路径')
    parser.add_argument('--nodes', type=int, default=2, help='计算节点数量')
    args = parser.parse_args()

    manager = SystemManager(args.config)
    
    try:
        # 启动各个组件
        manager.start_coordinator()
        time.sleep(2)  # 等待协调节点就绪
        
        manager.start_compute_nodes(args.nodes)
        time.sleep(2)  # 等待计算节点就绪
        
        manager.start_api_server()
        
        # 监控进程
        manager.monitor_processes()
    except KeyboardInterrupt:
        print("\n正在停止系统...")
        manager.stop_all()
    except Exception as e:
        print(f"系统启动失败: {str(e)}")
        manager.stop_all()

if __name__ == '__main__':
    main()
```