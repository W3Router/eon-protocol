```python
import argparse
import logging
from pathlib import Path
from typing import Dict, Any
import yaml
import uvicorn
from .api.service import create_app
from .core.node import CoordinatorNode, ComputeNode
from .utils.config import Config

def setup_logging(config: Dict[str, Any]):
    """配置日志系统"""
    logging.basicConfig(
        level=config.get('logging', {}).get('level', 'INFO'),
        format=config.get('logging', {}).get('format', 
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        filename=config.get('logging', {}).get('file')
    )

def load_config(config_path: str) -> Dict[str, Any]:
    """加载配置文件"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def start_coordinator(config: Dict[str, Any]):
    """启动协调节点"""
    coordinator = CoordinatorNode(config['coordinator'])
    coordinator.start()

def start_compute_node(config: Dict[str, Any]):
    """启动计算节点"""
    compute_node = ComputeNode(config['compute_node'])
    compute_node.start()

def start_api_server(config: Dict[str, Any]):
    """启动API服务器"""
    app = create_app(config)
    uvicorn.run(
        app,
        host=config['server']['host'],
        port=config['server']['port'],
        workers=config['server']['workers']
    )

def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(description='EON Protocol')
    parser.add_argument('--config', required=True, help='配置文件路径')
    parser.add_argument('--mode', choices=['coordinator', 'compute', 'api'], 
                       required=True, help='运行模式')
    args = parser.parse_args()

    # 加载配置
    config = load_config(args.config)
    setup_logging(config)
    logger = logging.getLogger(__name__)

    try:
        if args.mode == 'coordinator':
            logger.info("启动协调节点...")
            start_coordinator(config)
        elif args.mode == 'compute':
            logger.info("启动计算节点...")
            start_compute_node(config)
        elif args.mode == 'api':
            logger.info("启动API服务器...")
            start_api_server(config)
    except Exception as e:
        logger.error(f"启动失败: {str(e)}")
        raise

if __name__ == '__main__':
    main()
```